#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import traceback
from graphene import (
    String,
    Field,
    Mutation,
    Boolean,
    String,
    List,
    DateTime,
    Int,
    Decimal,
)
from silvaengine_utility import JSON
from .types import FunctionRequestType
from .handlers import insert_update_record_handler, delete_function_request_handler


class InsertUpdateRecord(Mutation):
    record = Field(FunctionRequestType)

    class Arguments:
        record_type = String(required=True)
        entity = JSON(required=True)
        transaction_record_type = String()
        request_id = String()

    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            record = insert_update_record_handler(info, **kwargs)
        except Exception:
            log = traceback.format_exc()
            info.context.get("logger").exception(log)
            raise

        return InsertUpdateRecord(record=record)


class DeleteFunctionRequest(Mutation):
    ok = Boolean()

    class Arguments:
        function_name = String(required=True)
        request_id = String(required=True)

    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            ok = delete_function_request_handler(info, **kwargs)
        except Exception:
            log = traceback.format_exc()
            info.context.get("logger").exception(log)
            raise

        return DeleteFunctionRequest(ok=ok)
