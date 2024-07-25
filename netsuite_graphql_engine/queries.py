#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from .handlers import (
    resolve_deleted_records_handler,
    resolve_record_by_variables_handler,
    resolve_record_handler,
    resolve_records_handler,
    resolve_select_values_handler,
    resolve_suiteql_result_handler,
)


def resolve_select_values(info, **kwargs):
    return resolve_select_values_handler(info, **kwargs)


def resolve_deleted_records(info, **kwargs):
    return resolve_deleted_records_handler(info, **kwargs)


def resolve_suiteql_result(info, **kwargs):
    return resolve_suiteql_result_handler(info, **kwargs)


def resolve_record(info, **kwargs):
    return resolve_record_handler(info, **kwargs)


def resolve_record_by_variables(info, **kwargs):
    return resolve_record_by_variables_handler(info, **kwargs)


def resolve_records(info, **kwargs):
    return resolve_records_handler(info, **kwargs)
