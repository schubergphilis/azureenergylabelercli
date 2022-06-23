#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: azureenergylabelercli.py
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
Main code for azureenergylabelercli.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import logging
import logging.config
import json
import argparse
import coloredlogs

from azureenergylabelerlib import (AzureEnergyLabeler,
                                   DEFAULT_DEFENDER_FOR_CLOUD_FRAMEWORKS,
                                   ALL_TENANT_EXPORT_TYPES,
                                   ALL_SUBSCRIPTION_EXPORT_DATA,
                                   SUBSCRIPTION_METRIC_EXPORT_TYPES,
                                   TENANT_THRESHOLDS,
                                   SUBSCRIPTION_THRESHOLDS,
                                   RESOURCE_GROUP_THRESHOLDS,
                                   TENANT_METRIC_EXPORT_TYPES)

from yaspin import yaspin
from .validators import ValidatePath, azure_subscription_id


__author__ = '''Sayantan Khanra <skhanra@schubergphilis.com>'''
__docformat__ = '''google'''
__date__ = '''04-05-2022'''
__copyright__ = '''Copyright 2022, Sayantan Khanra'''
__credits__ = ["Sayantan Khanra"]
__license__ = '''MIT'''
__maintainer__ = '''Sayantan Khanra'''
__email__ = '''<skhanra@schubergphilis.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".


# This is the main prefix used for logging
LOGGER_BASENAME = '''azureenergylabelercli'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


def get_arguments():
    """
    Gets us the cli arguments.

    Returns the args as parsed from the argsparser.
    """
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(description='''A cli to help generate energy label for
    Azure tenant, subscriptions and resource groups. ''')
    parser.add_argument('--log-config',
                        '-l',
                        action='store',
                        dest='logger_config',
                        help='The location of the logging config json file',
                        default='')
    parser.add_argument('--log-level',
                        '-L',
                        help='Provide the log level. Defaults to info.',
                        dest='log_level',
                        action='store',
                        default='info',
                        choices=['debug',
                                 'info',
                                 'warning',
                                 'error',
                                 'critical'])
    parser.add_argument('--tenant-id',
                        '-tid',
                        dest='tenant_id',
                        required=True,
                        type=str,
                        help='The ID of the Tenant to labeled')
    single_subscription_action = parser.add_argument('--single-subscription-id',
                                                     '-s',
                                                     required=False,
                                                     dest='single_subscription_id',
                                                     action='store',
                                                     type=azure_subscription_id,
                                                     help='Run the labeler on a single subscription.')
    parser.add_argument('--frameworks',
                        '-f',
                        default=["Azure Security Benchmark"],
                        nargs='*',
                        help='The list of applicable frameworks: \
                                    ["Azure Security Benchmark", "SOC TSP", "Azure CIS 1.1.0"], '
                             'default=["Azure Security Benchmark"]')
    subscription_list = parser.add_mutually_exclusive_group()
    subscription_list._group_actions.append(single_subscription_action)  # pylint: disable=protected-access
    subscription_list.add_argument('--allowed-subscription-ids',
                                   '-a',
                                   nargs='*',
                                   default=None,
                                   required=False,
                                   help='A list of Azure Subscription IDs for which an energy label will be produced. '
                                        'Mutually exclusive with '
                                        '--denied-subscription-ids and --single-subscription-id arguments.')
    subscription_list.add_argument('--denied-subscription-ids',
                                   '-d',
                                   nargs='*',
                                   default=None,
                                   required=False,
                                   help='A list of Azure Subscription IDs that will '
                                        'be excluded from producing the energy label. '
                                        'Mutually exclusive with '
                                        '--allowed-subscription-ids and --single-subscription-id arguments.')
    parser.add_argument('--export-path',
                        '-p',
                        action=ValidatePath,
                        required=False,
                        help='Exports a snapshot of chosen data in '
                             'JSON formatted files to the specified directory or Storage Account Container location.')
    export_options = parser.add_mutually_exclusive_group()
    export_options.add_argument('--export-metrics',
                                '-em',
                                action='store_const',
                                dest='export_all',
                                const=False,
                                help='Exports metrics/statistics along with findings data in '
                                     'JSON formatted files to the specified directory or '
                                     'Storage Account Container location.')
    export_options.add_argument('--export-all',
                                '-ea',
                                action='store_const',
                                dest='export_all',
                                const=True,
                                help='Exports metrics/statistics without sensitive findings data in '
                                     'JSON formatted files to the specified directory or '
                                     'Storage Account Container location.')
    parser.add_argument('--to-json',
                        '-j',
                        dest='to_json',
                        action='store_true',
                        required=False,
                        default=False,
                        help='Return the report in json format.')
    parser.set_defaults(export_all=True)
    args = parser.parse_args()
    return args


def setup_logging(level, config_file=None):
    """
    Sets up the logging.

    Needs the args to get the log level supplied

    Args:
        level: At which level do we log
        config_file: Configuration to use

    """
    # This will configure the logging, if the user has set a config file.
    # If there's no config file, logging will default to stdout.
    if config_file:
        # Get the config for the logger. Of course this needs exception
        # catching in case the file is not there and everything. Proper IO
        # handling is not shown here.
        try:
            with open(config_file) as conf_file:
                configuration = json.loads(conf_file.read())
                # Configure the logger
                logging.config.dictConfig(configuration)
        except ValueError:
            print(f'File "{config_file}" is not valid json, cannot continue.')
            raise SystemExit(1)
    else:
        coloredlogs.install(level=level.upper())


def wait_for_findings(method_name, method_argument, log_level):
    """If log level is not debug shows a spinner while the callable provided gets security hub findings.

    Args:
        method_name: The method to execute while waiting.
        method_argument: The argument to pass to the method.
        log_level: The log level as set by the user.

    Returns:
        findings: A list of defender for cloud findings as retrieved by the callable.

    """
    try:
        if not log_level == 'debug':
            with yaspin(text="Please wait while retrieving Defender For Cloud findings...", color="yellow") as spinner:
                findings = method_name(method_argument)
            spinner.ok("✅")
        else:
            findings = method_name(method_argument)
    except Exception as msg:
        LOGGER.error(msg)
        raise SystemExit(1)
    return findings


def get_tenant_reporting_data(tenant_id,
                              allowed_subscription_ids,
                              denied_subscription_ids,
                              export_all_data_flag,
                              log_level):
    """Gets the reporting data for a landing zone.

    Args:
        tenant_id: Tenant Id of the tenant
        allowed_subscription_ids: The allowed subscription ids for tenant inclusion if any.
        denied_subscription_ids: The denied subscription ids for tenant zone exclusion if any.
        export_all_data_flag: If set all data is going to be exported, else only basic reporting.
        log_level: The log level set.

    Returns:
        report_data, exporter_arguments

    """
    labeler = AzureEnergyLabeler(tenant_id=tenant_id,
                                 tenant_thresholds=TENANT_THRESHOLDS,
                                 resource_group_thresholds=RESOURCE_GROUP_THRESHOLDS,
                                 subscription_thresholds=SUBSCRIPTION_THRESHOLDS,
                                 frameworks=DEFAULT_DEFENDER_FOR_CLOUD_FRAMEWORKS,
                                 allowed_subscription_ids=allowed_subscription_ids,
                                 denied_subscription_ids=denied_subscription_ids)
    wait_for_findings(AzureEnergyLabeler.defender_for_cloud_findings.fget, labeler, log_level)
    report_data = [['Tenant ID:', tenant_id],
                   ['Tenant Security Score:', labeler.tenant_energy_label.label],
                   ['Tenant Percentage Coverage:', labeler.tenant_energy_label.coverage],
                   ['Labeled Subscriptions Measured:',
                    labeler.labeled_subscriptions_energy_label.subscriptions_measured]]
    if not labeler.tenant_energy_label.best_label == labeler.tenant_energy_label.worst_label:
        report_data.extend([['Best Subscription Security Score:', labeler.tenant_energy_label.best_label],
                            ['Worst Subscription Security Score:', labeler.tenant_energy_label.worst_label]])
    export_types = ALL_TENANT_EXPORT_TYPES if export_all_data_flag else TENANT_METRIC_EXPORT_TYPES
    exporter_arguments = {'export_types': export_types,
                          'id': tenant_id,
                          'energy_label': labeler.tenant_energy_label.label,
                          'defender_for_cloud_findings': labeler.defender_for_cloud_findings,
                          'labeled_subscriptions': labeler.tenant_labeled_subscriptions,
                          'credentials': labeler.tenant_credentials}
    return report_data, exporter_arguments


def get_subscription_reporting_data(
        tenant_id,
        subscription_id,
        export_all_data_flag,
        log_level):
    """Gets the reporting data for a single account.

    Args:
        tenant_id: Tenant Id of the tenant
        subscription_id: The ID of the subscription to get reporting on.
        export_all_data_flag: If set all data is going to be exported, else only basic reporting.
        log_level: The log level set.

    Returns:
        report_data, exporter_arguments

    """
    _allowed_subscription_ids = []
    _allowed_subscription_ids.append(subscription_id)
    labeler = AzureEnergyLabeler(tenant_id=tenant_id,
                                 tenant_thresholds=TENANT_THRESHOLDS,
                                 resource_group_thresholds=RESOURCE_GROUP_THRESHOLDS,
                                 subscription_thresholds=SUBSCRIPTION_THRESHOLDS,
                                 frameworks=DEFAULT_DEFENDER_FOR_CLOUD_FRAMEWORKS,
                                 allowed_subscription_ids=_allowed_subscription_ids)
    tenant = labeler.tenant
    defender_for_cloud_findings = wait_for_findings(AzureEnergyLabeler.defender_for_cloud_findings.fget,
                                                    labeler,
                                                    log_level)
    subscription = next(
        subscription for subscription in tenant.subscriptions if subscription.subscription_id == subscription_id)
    energy_label = subscription.get_energy_label(defender_for_cloud_findings)
    report_data = [['Subscription ID:', subscription.subscription_id],
                   ['Subscription Security Score:', energy_label.label],
                   ['Number Of High Findings:', energy_label.number_of_high_findings],
                   ['Number Of Medium Findings:', energy_label.number_of_medium_findings],
                   ['Number Of Low Findings:', energy_label.number_of_low_findings],
                   ['Max Days Open:', energy_label.max_days_open]]
    if subscription.display_name:
        report_data.insert(0, ['Subscription Display Name:', subscription.display_name])
    export_types = ALL_SUBSCRIPTION_EXPORT_DATA if export_all_data_flag else SUBSCRIPTION_METRIC_EXPORT_TYPES
    exporter_arguments = {'export_types': export_types,
                          'id': subscription.subscription_id,
                          'energy_label': energy_label.label,
                          'defender_for_cloud_findings': defender_for_cloud_findings,
                          'labeled_subscriptions': subscription,
                          'credentials': labeler.tenant_credentials}
    return report_data, exporter_arguments
