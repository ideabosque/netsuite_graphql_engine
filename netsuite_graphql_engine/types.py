#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import (
    ObjectType,
    Field,
    List,
    String,
    Int,
    Decimal,
    DateTime,
    Boolean,
)
from silvaengine_utility import JSON


class SelectValueType(ObjectType):
    value = String()
    value_id = String()


class SuiteqlResultType(ObjectType):
    count = Int()
    has_more = Boolean()
    offset = Int()
    total_results = Int()
    items = List(JSON)


class FunctionRequestType(ObjectType):
    function_name = String()
    request_id = String()
    account_id = String()
    record_type = String()
    variables = JSON()
    status = String()
    data = List(JSON)
    internal_ids = List(String)
    log = String()
    request_page_size = Int()
    request_page_number = Int()
    total_records = Int()
    created_at = DateTime()
    updated_at = DateTime()
    updated_by = String()
