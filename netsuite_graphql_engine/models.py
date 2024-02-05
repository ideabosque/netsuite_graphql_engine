#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import os
from pynamodb.models import Model
from pynamodb.attributes import (
    ListAttribute,
    MapAttribute,
    NumberAttribute,
    UnicodeAttribute,
    UTCDateTimeAttribute,
    BooleanAttribute,
)
from pynamodb.indexes import GlobalSecondaryIndex, LocalSecondaryIndex, AllProjection
from silvaengine_dynamodb_base import BaseModel


class FunctionNameAccountIdIndex(LocalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "account_id-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    function_name = UnicodeAttribute(hash_key=True)
    account_id = UnicodeAttribute(range_key=True)


class FunctionRequestModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "nge-function_request"

    function_name = UnicodeAttribute(hash_key=True)
    request_id = UnicodeAttribute(range_key=True)
    account_id = UnicodeAttribute()
    record_type = UnicodeAttribute()
    internal_ids = ListAttribute()
    variables = MapAttribute()
    status = UnicodeAttribute(default="initial")
    log = UnicodeAttribute(null=True)
    updated_by = UnicodeAttribute(default="system")
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()
    account_id_index = FunctionNameAccountIdIndex()


class RecordTypeUpdatedAtIndex(LocalSecondaryIndex):
    class Meta:
        # index_name is optional, but can be provided to override the default name
        index_name = "updated_at-index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    account_id_record_type = UnicodeAttribute(hash_key=True)
    updated_at = UnicodeAttribute(range_key=True)


class RecordStagingModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "nge-record_stagging"

    account_id_record_type = UnicodeAttribute(hash_key=True)
    internal_id = UnicodeAttribute(range_key=True)
    data = MapAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()
    updated_by = UnicodeAttribute(default="system")
    updated_at_index = RecordTypeUpdatedAtIndex()
