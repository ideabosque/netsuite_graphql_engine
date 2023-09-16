#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import functools, inspect, uuid, boto3, traceback, copy, time, asyncio
import concurrent.futures
from datetime import datetime, timedelta
from deepdiff import DeepDiff
from decimal import Decimal
from pytz import timezone
from silvaengine_utility import Utility
from suitetalk_connector import SOAPConnector, RESTConnector
from .types import SelectValueType, FunctionRequestType
from .models import FunctionRequestModel, RecordStagingModel

datetime_format = "%Y-%m-%dT%H:%M:%S%z"
soap_connector = None
rest_connector = None
default_timezone = None
aws_lambda = None
async_function_name = None
async_functions = {}
txmap = {}


class FunctionError(Exception):
    pass


def handlers_init(logger, **setting):
    global soap_connector, rest_connector, default_timezone, aws_lambda, async_function_name, async_functions, txmap
    soap_connector = SOAPConnector(logger, **setting)
    rest_connector = RESTConnector(logger, **setting)
    default_timezone = setting.get("TIMEZONE", "UTC")
    aws_lambda = boto3.client(
        "lambda",
        region_name=setting.get("region_name"),
        aws_access_key_id=setting.get("aws_access_key_id"),
        aws_secret_access_key=setting.get("aws_secret_access_key"),
    )
    async_function_name = setting.get("ASYNC_FUNCTION_NAME")
    async_functions = setting.get("ASYNC_FUNCTIONS")
    txmap = setting.get("TXMAP")


def funct_decorator(cache_duration=1):
    def actual_decorator(original_function):
        @functools.wraps(original_function)
        def wrapper_function(*args, **kwargs):
            kwargs.update(
                {"function_name": original_function.__name__.replace("_handler", "")}
            )
            if kwargs.get("cache_duration") is None:
                kwargs.update({"cache_duration": cache_duration})

            try:
                request_page_size = int(kwargs.get("request_page_size", 10))
                request_page_number = int(kwargs.get("request_page_number", 1))
                function_request, data = original_function(*args, **kwargs)
                manual_dispatch = kwargs.get("manual_dispatch", False)

                ## Dispatch the request to the lambda worker to get the data.
                if function_request.status == "initial" and not manual_dispatch:
                    function_request.update(
                        actions=[
                            FunctionRequestModel.status.set("in_progress"),
                            FunctionRequestModel.updated_at.set(
                                datetime.now(tz=timezone("UTC"))
                            ),
                        ]
                    )
                    dispatch_async_function(
                        args[0].context.get("logger"),
                        async_functions.get(function_request.function_name),
                        function_request.request_id,
                        endpoint_id=args[0].context.get("endpoint_id"),
                    )

                if function_request.status == "initial" and manual_dispatch:
                    function_request.update(
                        actions=[
                            FunctionRequestModel.status.set("manual_dispatch"),
                            FunctionRequestModel.updated_at.set(
                                datetime.now(tz=timezone("UTC"))
                            ),
                        ]
                    )

                function_request_type = {
                    "function_name": function_request.function_name,
                    "request_id": function_request.request_id,
                    "record_type": function_request.record_type,
                    "variables": function_request.variables.__dict__[
                        "attribute_values"
                    ],
                    "status": function_request.status,
                    "internal_ids": function_request.internal_ids,
                    "log": function_request.log,
                    "request_page_size": request_page_size,
                    "request_page_number": request_page_number,
                    "total_records": len(function_request.internal_ids),
                    "created_at": function_request.created_at,
                    "updated_at": function_request.updated_at,
                }
                if data is not None:
                    function_request_type.update({"data": data})

                return FunctionRequestType(**function_request_type)
            except:
                log = traceback.format_exc()
                args[0].context.get("logger").exception(log)
                raise

        return wrapper_function

    return actual_decorator


def async_decorator(original_function):
    @functools.wraps(original_function)
    def wrapper_function(*args, **kwargs):
        function_name = original_function.__name__.replace(
            "_async_handler", ""
        ).replace("get", "resolve")

        try:
            function_request = FunctionRequestModel.get(
                function_name, kwargs.get("request_id")
            )

            kwargs.update({"function_request": function_request})
            result = original_function(*args, **kwargs)

            if isinstance(result, list):
                internal_ids = set(function_request.internal_ids + result)
                function_request.update(
                    actions=[
                        FunctionRequestModel.internal_ids.set(internal_ids),
                        FunctionRequestModel.status.set("success"),
                        FunctionRequestModel.log.set(None),
                        FunctionRequestModel.updated_at.set(
                            datetime.now(tz=timezone("UTC"))
                        ),
                    ]
                )
                return result

            assert isinstance(result, dict), "The result must be a dict instance."

            ## Since the async search is not finished, dispatch the function to check later.
            if result.get("job_id"):
                log = f"Job ID {result['job_id']}: status ({result['status']}) at percent completed ({result['percent_completed']}) with estimated time to complete ({result['est_remaining_duration']})."
                variables = dict(
                    function_request.variables.__dict__["attribute_values"],
                    **{"job_id": result.get("job_id")},
                )
                function_request.update(
                    actions=[
                        FunctionRequestModel.variables.set(variables),
                        FunctionRequestModel.log.set(log),
                        FunctionRequestModel.updated_at.set(
                            datetime.now(tz=timezone("UTC"))
                        ),
                    ]
                )

                if (
                    result["status"] == "processing"
                    and result["est_remaining_duration"] > 0
                ):
                    # time.sleep(result["est_remaining_duration"])
                    time.sleep(30)
                dispatch_async_function(
                    args[0],
                    async_functions.get(function_request.function_name),
                    function_request.request_id,
                    endpoint_id=kwargs.get("endpoint_id"),
                )
                return result

            ## Process the async search result.
            assert result.get("search_id") and result.get(
                "page_index"
            ), "The search_id and page_index are required."

            if result["page_index"] == 1:
                log = f"Total_records/Total_pages {result['total_records']}/{result['total_pages']}: {len(result['records'])} records at page {result['page_index']}."
                function_request.update(
                    actions=[
                        FunctionRequestModel.internal_ids.set(result["records"]),
                        FunctionRequestModel.log.set(log),
                        FunctionRequestModel.updated_at.set(
                            datetime.now(tz=timezone("UTC"))
                        ),
                    ]
                )
                dispatch_async_function(
                    args[0],
                    async_functions.get(function_request.function_name),
                    function_request.request_id,
                    total_pages=result["total_pages"],
                    endpoint_id=kwargs.get("endpoint_id"),
                )
                return result

            return dict(result, **{"request_name": function_request.function_name})

        except:
            log = traceback.format_exc()
            args[0].context.get("logger").exception(log)
            function_request.update(
                actions=[
                    FunctionRequestModel.status.set("failed"),
                    FunctionRequestModel.log.set(log),
                    FunctionRequestModel.updated_at.set(
                        datetime.now(tz=timezone("UTC"))
                    ),
                ]
            )
            raise

    return wrapper_function


def monitor_decorator(original_function):
    @functools.wraps(original_function)
    def wrapper_function(*args, **kwargs):
        # Get the signature of the original function
        signature = inspect.signature(original_function)
        # Get the parameter names from the signature
        parameter_names = list(signature.parameters.keys())

        if "info" in parameter_names:
            logger = args[0].context.get("logger")
        elif "logger" in parameter_names:
            logger = args[0]

        logger.info(
            f"Start function: {original_function.__name__} at {time.strftime('%X')}!!"
        )
        result = original_function(*args, **kwargs)
        logger.info(
            f"End function: {original_function.__name__} at {time.strftime('%X')}!!"
        )
        return result

    return wrapper_function


def transform_value(key, value):
    if key not in txmap.keys():
        return value

    tx_funct = lambda value: eval(txmap[key])
    return tx_funct(value)


def object_to_dict(obj):
    def handle_value(value):
        if isinstance(value, list):
            return [handle_value(item) for item in value]
        elif isinstance(value, dict):
            return {key: handle_value(val) for key, val in value.items()}
        elif hasattr(value, "__dict__"):
            return object_to_dict(value)
        elif isinstance(value, datetime):
            return value.strftime(datetime_format)  # You should define datetime_format
        else:
            return value

    if not hasattr(obj, "__dict__"):
        raise ValueError("The input is not an object with attributes.")

    obj_dict = {}
    for key, value in obj.__dict__["__values__"].items():
        if value is None:
            continue

        obj_dict[key] = transform_value(key, handle_value(value))
    return obj_dict


def convert_values(kwargs):
    def convert(value):
        if isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, datetime):
            return datetime.strftime(value, datetime_format)
        elif isinstance(value, list):
            return [
                convert(item) if not isinstance(item, dict) else convert_dict(item)
                for item in value
            ]
        elif isinstance(value, dict):
            return convert_dict(value)
        else:
            return value

    def convert_dict(d):
        return {k: convert(v) for k, v in d.items()}

    return convert_dict(kwargs)


# Define your asynchronous function here (async_function)
async def async_function(logger, async_function, request_id, page_index):
    # Your asynchronous code here
    params = {"request_id": str(request_id), "page_index": page_index}
    return eval(f"{async_function.replace('netsuite_', '')}_handler")(logger, **params)


# Define a wrapper function for the asynchronous task
async def dispatch_async_function_wrapper(
    logger, async_function, request_id, page_index
):
    await async_function(logger, async_function, request_id, page_index)


def dispatch_async_function(
    logger, async_function, request_id, total_pages=None, endpoint_id=None
):
    ## Dispatch the sync tasks to collect the async result.
    if total_pages:
        # Create a list to store the tasks
        tasks = []

        # Create a multiprocessing Pool
        with concurrent.futures.ProcessPoolExecutor() as executor:
            # Dispatch asynchronous tasks to different processes for each page index
            for i in range(2, total_pages + 1):
                tasks.append(
                    executor.submit(
                        asyncio.run,
                        dispatch_async_function_wrapper(
                            logger, async_function, request_id, i
                        ),
                    )
                )

        # Gather the tasks from the processes
        gathered_results = [task.result() for task in tasks]
        function_request = FunctionRequestModel.get(
            gathered_results[0]["function_name"], request_id
        )

        internal_id_list = [entry["internal_ids"] for entry in gathered_results]
        internal_ids = set(
            function_request.internal_ids
            + [internal_id for sublist in internal_id_list for internal_id in sublist]
        )

        function_request.update(
            actions=[
                FunctionRequestModel.internal_ids.set(internal_ids),
                FunctionRequestModel.status.set("success"),
                FunctionRequestModel.log.set(None),
                FunctionRequestModel.updated_at.set(datetime.now(tz=timezone("UTC"))),
            ]
        )

    params = {"request_id": str(request_id)}
    if endpoint_id is None:
        eval(f"{async_function.replace('netsuite_', '')}_handler")(logger, **params)
        return

    payload = {
        "endpoint_id": endpoint_id,
        "funct": async_function,
        "params": params,
    }
    response = aws_lambda.invoke(
        FunctionName=async_function_name,
        InvocationType="Event",
        Payload=Utility.json_dumps(payload),
    )
    if "FunctionError" in response.keys():
        log = Utility.json_loads(response["Payload"].read())
        raise FunctionError(log)


def get_data_detail(info, record_type, internal_ids):
    if len(internal_ids) == 0:
        return []
    results = RecordStagingModel.updated_at_index.query(
        record_type,
        RecordStagingModel.internal_id.is_in(*internal_ids),
    )
    return [record.data.__dict__["attribute_values"] for record in results]


def extract_requested_fields(info):
    # Accessing the field nodes to determine the requested fields
    field_nodes = info.field_asts[0].selection_set.selections

    # Function to recursively extract fields from fragments and selections
    def extract_fields(selection_set):
        fields = []
        for selection in selection_set:
            if type(selection).__name__ == "Field":
                fields.append(selection.name.value)
                if selection.selection_set:
                    fields.extend(extract_fields(selection.selection_set.selections))
            elif type(selection).__name__ == "FragmentSpread":
                fragment = info.fragments[selection.name.value]
                fields.extend(extract_fields(fragment.selection_set.selections))
            elif type(selection).__name__ == "InlineFragment":
                fields.extend(extract_fields(selection.selection_set.selections))
            else:
                continue
        return fields

    requested_fields = extract_fields(field_nodes)
    return requested_fields


def get_function_request(info, **kwargs):
    record_type = kwargs.pop("record_type")
    request_id = kwargs.pop("request_id", None)
    function_name = kwargs.pop("function_name")
    cache_duration = float(kwargs.pop("cache_duration"))
    request_page_size = int(kwargs.get("request_page_size", 10))
    request_page_number = int(kwargs.get("request_page_number", 1))
    start_idx = (request_page_number - 1) * request_page_size
    end_idx = start_idx + request_page_size

    requested_fields = extract_requested_fields(info)
    data_detail = "data" in requested_fields

    if request_id:
        function_request = FunctionRequestModel.get(function_name, request_id)

        data = (
            get_data_detail(
                info, record_type, function_request.internal_ids[start_idx:end_idx]
            )
            if data_detail
            else None
        )
        return function_request, data

    variables = convert_values(kwargs)
    results = FunctionRequestModel.query(
        function_name,
        None,
        (
            FunctionRequestModel.updated_at
            >= datetime.now(tz=timezone("UTC")) - timedelta(hours=cache_duration)
        ),
    )
    entities = [entity for entity in results]
    if len(entities) > 0:
        last_entity = max(entities, key=lambda x: x.updated_at)
        diff_data = DeepDiff(
            Utility.json_loads(
                Utility.json_dumps(last_entity.variables.__dict__["attribute_values"])
            ),
            Utility.json_loads(Utility.json_dumps(variables)),
            ignore_order=True,
        )
        if diff_data == {}:
            data = (
                get_data_detail(
                    info, record_type, last_entity.internal_ids[start_idx:end_idx]
                )
                if data_detail
                else None
            )
            return last_entity, data

    request_id = str(uuid.uuid1().int >> 64)
    FunctionRequestModel(
        function_name,
        request_id,
        **{
            "record_type": record_type,
            "variables": variables,
            "internal_ids": [],
            "created_at": datetime.now(tz=timezone("UTC")),
            "updated_at": datetime.now(tz=timezone("UTC")),
        },
    ).save()

    function_request = FunctionRequestModel.get(function_name, request_id)
    return function_request, [] if data_detail else None


@monitor_decorator
def get_select_values(info, **kwargs):
    record_type = kwargs.get("record_type")
    field = kwargs.get("field")
    sublist = kwargs.get("sublist")
    try:
        if soap_connector.lookup_select_values[field].get("values"):
            return soap_connector.lookup_select_values[field]["values"]

        if record_type.find("customlist") == 0:
            record = soap_connector.get_custom_list(record_type)
            if record:
                return {
                    element.value: element.valueId
                    for element in record.customValueList.customValue
                }
            return {}

        return soap_connector.get_select_values(record_type, field, sublist=sublist)
    except:
        log = traceback.format_exc()
        info.context.get("logger").exception(log)
        raise


def resolve_select_values_handler(info, **kwargs):
    select_values = get_select_values(info, **kwargs)
    return [
        SelectValueType(**{"value": k, "value_id": v}) for k, v in select_values.items()
    ]


def insert_update_record_staging(logger, record_type, record):
    try:
        count = RecordStagingModel.count(
            record_type,
            RecordStagingModel.internal_id == record.internalId,
        )
        if count == 0:
            RecordStagingModel(
                record_type,
                record.internalId,
                **{
                    "data": object_to_dict(record),
                    "created_at": datetime.now(tz=timezone("UTC")),
                    "updated_at": datetime.now(tz=timezone("UTC")),
                },
            ).save()
        else:
            record_staging = RecordStagingModel.get(record_type, record.internalId)
            record_staging.update(
                actions=[
                    RecordStagingModel.data.set(object_to_dict(record)),
                    RecordStagingModel.updated_at.set(datetime.now(tz=timezone("UTC"))),
                ]
            )
    except:
        log = traceback.format_exc()
        logger.exception(log)
        logger.info(Utility.json_dumps(object_to_dict(record)))
        raise


@monitor_decorator
@async_decorator
def get_record_async_handler(logger, **kwargs):
    function_request = kwargs.get("function_request")
    record = soap_connector.get_record(
        function_request.record_type,
        function_request.variables["id"],
        use_external_id=function_request.variables.__dict__["attribute_values"].get(
            "use_external_id", False
        ),
    )
    insert_update_record_staging(logger, function_request.record_type, record)

    return [record.internalId]


@funct_decorator(cache_duration=1)
def resolve_record_handler(info, **kwargs):
    return get_function_request(info, **kwargs)


@monitor_decorator
@async_decorator
def get_record_by_variables_async_handler(logger, **kwargs):
    function_request = kwargs.get("function_request")
    variables = {
        function_request.variables["field"]: function_request.variables["value"],
    }
    if function_request.variables.__dict__["attribute_values"].get("operator"):
        variables["operator"] = function_request.variables["operator"]
    record = soap_connector.get_record_by_variables(
        function_request.record_type, **variables
    )
    if record is not None:
        insert_update_record_staging(logger, function_request.record_type, record)

        return [record.internalId]
    return []


@funct_decorator(cache_duration=1)
def resolve_record_by_variables_handler(info, **kwargs):
    return get_function_request(info, **kwargs)


@monitor_decorator
@async_decorator
def get_records_async_handler(logger, **kwargs):
    function_request = kwargs.get("function_request")
    variables = copy.deepcopy(function_request.variables.__dict__["attribute_values"])

    ## If job_id and page_index are provided, then return the async result.
    if variables.get("job_id") and kwargs.get("page_index"):
        kwargs.update({"job_id": variables.get("job_id")})
        return get_records_async_result(logger, function_request.record_type, **kwargs)

    ## If job_id is provided only, then check the status of the async job.
    if variables.get("job_id"):
        result = soap_connector.check_async_status(variables.get("job_id"))
        if result["status"] != "finished":
            logger.info(
                f"Job ID {result['job_id']}: status ({result['status']}) at percent completed ({result['percent_completed']}) with estimated time to complete ({result['est_remaining_duration']})."
            )
            return result
        kwargs.update({"job_id": variables.get("job_id")})
        return get_records_async_result(logger, function_request.record_type, **kwargs)

    record_type = function_request.record_type

    hours = variables.get("hours", 0.0)
    cut_date = datetime.strptime(variables.get("cut_date"), datetime_format)
    end_date = datetime.now(tz=timezone(default_timezone))

    if hours > 0.0:
        end_date = cut_date + timedelta(hours=hours)

    variables = dict(
        variables,
        **{
            "cut_date": cut_date.strftime(datetime_format),
            "end_date": end_date.strftime(datetime_format),
            "async": True,
        },
    )

    if record_type in ["salesOrder", "purchaseOrder"]:
        result = soap_connector.get_transaction_result(record_type, **variables)
        info.context.get("logger").info(
            f"Job ID {result['job_id']}: status ({result['status']}) at percent completed ({result['percent_completed']}) with estimated time to complete ({result['est_remaining_duration']})."
        )
        return result
    elif record_type in ["inventoryLot"]:
        result = soap_connector.get_item_result(record_type, **variables)
        logger.info(
            f"Job ID {result['job_id']}: status ({result['status']}) at percent completed ({result['percent_completed']}) with estimated time to complete ({result['est_remaining_duration']})."
        )
        return result
    else:
        raise Exception(f"Unsupported record type ({record_type}).")


def get_records_async_result(logger, record_type, **kwargs):
    result = soap_connector.get_async_result(
        kwargs.get("job_id"), kwargs.get("page_index", 1)
    )
    logger.info(
        f"Total_records/Total_pages {result['total_records']}/{result['total_pages']}: {len(result['records'])} records at page {result['page_index']}."
    )

    if result["total_records"] == 0:
        return []

    kwargs.update({"limit": 1000})
    if record_type in ["salesOrder", "purchaseOrder"]:
        records = soap_connector.get_transactions(
            record_type, result["records"], **kwargs
        )
    elif record_type in ["inventoryLot"]:
        records = soap_connector.get_items(record_type, result["records"], **kwargs)
    else:
        raise Exception(f"Unsupported record type ({record_type}).")

    internal_ids = []
    for record in records:
        insert_update_record_staging(logger, record_type, record)
        internal_ids.append(record.internalId)

    if result["total_pages"] == 1:
        return internal_ids

    return {
        "search_id": result["search_id"],
        "total_records": result["total_records"],
        "total_pages": result["total_pages"],
        "page_index": result["page_index"],
        "internal_ids": internal_ids,
    }


@funct_decorator(cache_duration=1)
def resolve_records_handler(info, **kwargs):
    return get_function_request(info, **kwargs)


@monitor_decorator
@async_decorator
def insert_update_record_async_handler(logger, **kwargs):
    function_request = kwargs.get("function_request")
    variables = copy.deepcopy(function_request.variables.__dict__["attribute_values"])
    record_type = function_request.record_type
    if record_type in ["salesOrder", "purchaseOrder"]:
        tran_id = soap_connector.insert_update_transaction(
            record_type, variables["entity"]
        )
        record = soap_connector.get_record_by_variables(
            record_type, **{"tranId": tran_id, "operator": "is"}
        )
    elif record_type in ["customer", "vendor", "contact"]:
        internal_id = soap_connector.insert_update_person(
            record_type, variables["entity"]
        )
        record = soap_connector.get_record(
            record_type,
            internal_id,
        )
    elif record_type in ["lotNumberedInventoryItem"]:
        internal_id = soap_connector.insert_update_item(
            record_type, variables["entity"]
        )
        record = soap_connector.get_record(
            record_type,
            internal_id,
        )
    elif record_type == "task":
        internal_id = soap_connector.insert_update_task(
            variables["transaction_record_type"], variables["entity"]
        )
        record = soap_connector.get_record(
            record_type,
            internal_id,
        )
    else:
        raise Exception(f"Unsupported record type ({record_type}).")

    insert_update_record_staging(logger, record_type, record)

    return [record.internalId]


@funct_decorator(cache_duration=0)
def insert_update_record_handler(info, **kwargs):
    return get_function_request(info, **kwargs)
