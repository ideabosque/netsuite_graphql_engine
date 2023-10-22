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


# Hook function applied to deployment
def deploy() -> list:
    return [
        {
            "service": "netsuite",
            "class": "NetSuiteGraphQLEngine",
            "functions": {
                "netsuite_get_record_async": {
                    "is_static": False,
                    "label": "NetSuite Get Record Async",
                    "query": [],
                    "mutation": [],
                    "type": "RequestResponse",
                    "support_methods": ["POST"],
                    "is_auth_required": False,
                    "is_graphql": False,
                    "settings": "netsuite_graphql_engine",
                    "disabled_in_resources": True,  # Ignore adding to resource list.
                },
                "netsuite_get_record_by_variables_async": {
                    "is_static": False,
                    "label": "NetSuite Get Record By Variables Async",
                    "query": [],
                    "mutation": [],
                    "type": "RequestResponse",
                    "support_methods": ["POST"],
                    "is_auth_required": False,
                    "is_graphql": False,
                    "settings": "beta_core_api",
                    "disabled_in_resources": True,  # Ignore adding to resource list.
                },
                "netsuite_get_records_async": {
                    "is_static": False,
                    "label": "NetSuite Get Records Async",
                    "query": [],
                    "mutation": [],
                    "type": "RequestResponse",
                    "support_methods": ["POST"],
                    "is_auth_required": False,
                    "is_graphql": False,
                    "settings": "beta_core_api",
                    "disabled_in_resources": True,  # Ignore adding to resource list.
                },
                "netsuite_insert_update_record_async": {
                    "is_static": False,
                    "label": "NetSuite Insert Update Record Async",
                    "query": [],
                    "mutation": [],
                    "type": "RequestResponse",
                    "support_methods": ["POST"],
                    "is_auth_required": False,
                    "is_graphql": False,
                    "settings": "beta_core_api",
                    "disabled_in_resources": True,  # Ignore adding to resource list.
                },
                "netsuite_graphql": {
                    "is_static": False,
                    "label": "NetSuite GraphQL",
                    "query": [
                        {
                            "action": "selectValues",
                            "label": "View Select Values",
                        },
                        {
                            "action": "record",
                            "label": "View Record",
                        },
                        {
                            "action": "recordByVariables",
                            "label": "View Record By Variables",
                        },
                        {
                            "action": "records",
                            "label": "View Records",
                        },
                    ],
                    "mutation": [
                        {
                            "action": "insertUpdateRecord",
                            "label": "Create Update Record",
                        },
                    ],
                    "type": "RequestResponse",
                    "support_methods": ["POST"],
                    "is_auth_required": False,
                    "is_graphql": True,
                    "settings": "netsuite_graphql_engine",
                    "disabled_in_resources": True,  # Ignore adding to resource list.
                },
            },
        }
    ]


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
