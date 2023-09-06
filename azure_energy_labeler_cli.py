#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: azure_energy_labeler_cli.py
#
# Copyright 2022 Sayantan Khanra
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#

"""
Main code for azure_energy_labeler_cli.

.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html

"""

import logging
import json
from art import text2art
from terminaltables import AsciiTable
from azureenergylabelerlib import DataExporter
from azureenergylabelercli import (get_arguments,
                                   setup_logging,
                                   get_tenant_reporting_data,
                                   get_subscription_reporting_data)

__author__ = '''Sayantan Khanra <skhanra@schubergphilis.com>'''
__docformat__ = '''google'''
__date__ = '''22-04-2022'''
__copyright__ = '''Copyright 2022, Sayantan Khanra'''
__credits__ = ["Sayantan Khanra"]
__license__ = '''MIT'''
__maintainer__ = '''Sayantan Khanra'''
__email__ = '''<skhanra@schubergphilis.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".

# This is the main prefix used for logging
LOGGER_BASENAME = '''azure_energy_labeler_cli'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


def _get_reporting_arguments(args):
    method_arguments = {'export_all_data_flag': args.export_all,
                        'tenant_id': args.tenant_id,
                        'frameworks': args.frameworks,
                        'log_level': args.log_level,
                        'disable_spinner': args.disable_spinner}
    if args.single_subscription_id:
        get_reporting_data = get_subscription_reporting_data
        method_arguments.update({'subscription_id': args.single_subscription_id})
    else:
        get_reporting_data = get_tenant_reporting_data
        method_arguments.update({'allowed_subscription_ids': args.allowed_subscription_ids,
                                 'denied_subscription_ids': args.denied_subscription_ids,
                                 'denied_resource_group_names': args.denied_resource_group_names})
    return get_reporting_data(**method_arguments)


def report(report_data, to_json=False):
    """Report to table or json."""
    if to_json:
        data = {key.replace(':', '').replace(' ', '_').lower(): value for key, value in dict(report_data).items()}
        print(json.dumps(data, indent=2))
        return None
    table_data = [['Energy label report']]
    table_data.extend(report_data)
    table = AsciiTable(table_data)
    print(table.table)
    return None


def main():
    """Main method."""
    args = get_arguments()
    setup_logging(args.log_level, args.logger_config)
    logging.getLogger('botocore').setLevel(logging.ERROR)
    try:
        if not args.disable_banner:
            print(text2art("Azure Energy Labeler"))
        report_data, exporter_arguments = _get_reporting_arguments(args)
        if args.export_path:
            LOGGER.info(f'Trying to export data to the requested path : {args.export_path}')
            exporter = DataExporter(**exporter_arguments)
            exporter.export(args.export_path)
        report(report_data, args.to_json)
    except Exception as msg:
        LOGGER.error(msg)
        raise SystemExit(1) from None
    raise SystemExit(0)


if __name__ == '__main__':
    main()
