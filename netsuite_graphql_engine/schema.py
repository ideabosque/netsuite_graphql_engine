#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import time

from graphene import Boolean, DateTime, Decimal, Field, Int, List, ObjectType, String

from silvaengine_utility import JSON

from .mutations import DeleteFunctionRequest, InsertUpdateRecord
from .queries import (
    resolve_deleted_records,
    resolve_record,
    resolve_record_by_variables,
    resolve_records,
    resolve_select_values,
    resolve_suiteql_result,
)
from .types import (
    DeletedRecordType,
    FunctionRequestType,
    SelectValueType,
    SuiteqlResultType,
)


def type_class():
    return [SelectValueType, DeletedRecordType, SuiteqlResultType, FunctionRequestType]


class Query(ObjectType):
    ping = String()

    select_values = List(
        SelectValueType,
        record_type=String(required=True),
        field=String(required=True),
        sublist=String(),
    )

    deleted_records = List(
        DeletedRecordType,
        record_type=String(required=True),
        cut_date=String(required=True),
        end_date=String(required=True),
    )

    suiteql_result = Field(
        SuiteqlResultType,
        suiteql=String(required=True),
        limit=Int(),
        offset=Int(),
    )

    record = Field(
        FunctionRequestType,
        record_type=String(required=True),
        request_id=String(),
        cache_duration=Decimal(),
        variables=JSON(required=True),
        requested_by=String(),
    )

    record_by_variables = Field(
        FunctionRequestType,
        record_type=String(required=True),
        request_id=String(),
        cache_duration=Decimal(),
        variables=JSON(required=True),
        requested_by=String(),
    )

    records = Field(
        FunctionRequestType,
        record_type=String(required=True),
        request_id=String(),
        cache_duration=Decimal(),
        variables=JSON(required=True),
        requested_by=String(),
    )

    def resolve_ping(self, info):
        return f"Hello at {time.strftime('%X')}!!"

    def resolve_select_values(self, info, **kwargs):
        return resolve_select_values(info, **kwargs)

    def resolve_deleted_records(self, info, **kwargs):
        return resolve_deleted_records(info, **kwargs)

    def resolve_suiteql_result(self, info, **kwargs):
        return resolve_suiteql_result(info, **kwargs)

    def resolve_record(self, info, **kwargs):
        return resolve_record(info, **kwargs)

    def resolve_record_by_variables(self, info, **kwargs):
        return resolve_record_by_variables(info, **kwargs)

    def resolve_records(self, info, **kwargs):
        return resolve_records(info, **kwargs)


class Mutations(ObjectType):
    insert_update_record = InsertUpdateRecord.Field()
    delete_function_request = DeleteFunctionRequest.Field()
