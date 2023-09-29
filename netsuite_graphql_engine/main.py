#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import Schema
from .schema import Query, Mutations, type_class
from .handlers import (
    handlers_init,
    get_record_async_handler,
    get_record_by_variables_async_handler,
    get_records_async_handler,
    insert_update_record_async_handler,
)
from silvaengine_dynamodb_base import SilvaEngineDynamoDBBase


class NetSuiteGraphQLEngine(SilvaEngineDynamoDBBase):
    def __init__(self, logger, **setting):
        handlers_init(logger, **setting)

        self.logger = logger
        self.setting = setting

        SilvaEngineDynamoDBBase.__init__(self, logger, **setting)

    def netsuite_get_record_async(self, **params):
        get_record_async_handler(self.logger, **params)

    def netsuite_get_record_by_variables_async(self, **params):
        get_record_by_variables_async_handler(self.logger, **params)

    def netsuite_get_records_async(self, **params):
        get_records_async_handler(self.logger, **params)

    def netsuite_insert_update_record_async(self, **params):
        insert_update_record_async_handler(self.logger, **params)

    def netsuite_graphql(self, **params):
        schema = Schema(
            query=Query,
            mutation=Mutations,
            types=type_class(),
        )
        return self.graphql_execute(schema, **params)
