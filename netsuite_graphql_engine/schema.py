#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import time
from graphene import ObjectType, String, List, Field, Int, DateTime, Boolean, Decimal
from .types import SelectValueType, FunctionRequestType
from .mutations import InsertUpdateRecord, DeleteFunctionRequest
from .queries import (
    resolve_select_values,
    resolve_record,
    resolve_record_by_variables,
    resolve_records,
)


def type_class():
    return [SelectValueType, FunctionRequestType]


class Query(ObjectType):
    ping = String()

    select_values = List(
        SelectValueType,
        record_type=String(required=True),
        field=String(required=True),
        sublist=String(),
    )

    record = Field(
        FunctionRequestType,
        record_type=String(required=True),
        id=String(required=True),
        use_external_id=Boolean(),
        request_id=String(),
        cache_duration=Decimal(),
    )

    record_by_variables = Field(
        FunctionRequestType,
        record_type=String(required=True),
        field=String(required=True),
        value=String(required=True),
        operator=String(),
        request_id=String(),
        cache_duration=Decimal(),
    )

    records = Field(
        FunctionRequestType,
        record_type=String(required=True),
        cut_date=String(),
        hours=Decimal(),
        vendor_id=String(),
        subsidiary=String(),
        item_detail=Boolean(),
        inventory_detail=Boolean(),
        internal_ids=List(String),
        request_id=String(),
        cache_duration=Decimal(),
        data_detail=Boolean(),
        manual_dispatch=Boolean(),
        request_page_size=Int(),
        request_page_number=Int(),
    )

    def resolve_ping(self, info):
        return f"Hello at {time.strftime('%X')}!!"

    def resolve_select_values(self, info, **kwargs):
        return resolve_select_values(info, **kwargs)

    def resolve_record(self, info, **kwargs):
        return resolve_record(info, **kwargs)

    def resolve_record_by_variables(self, info, **kwargs):
        return resolve_record_by_variables(info, **kwargs)

    def resolve_records(self, info, **kwargs):
        return resolve_records(info, **kwargs)


class Mutations(ObjectType):
    insert_update_record = InsertUpdateRecord.Field()
    delete_function_request = DeleteFunctionRequest.Field()
