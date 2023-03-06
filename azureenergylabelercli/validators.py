#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: validators.py
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
Main code for validators.

.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html
"""

import argparse
import logging

from argparse import ArgumentTypeError

from azureenergylabelerlib import (is_valid_subscription_id,
                                   DestinationPath)

from .azureenergylabelercliexceptions import (MissingRequiredArguments,
                                              MutuallyExclusiveArguments)


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
LOGGER_BASENAME = '''validators'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


class ValidatePath(argparse.Action):
    """Validates a given path."""

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        destination = DestinationPath(values)
        if not destination.is_valid():
            raise argparse.ArgumentTypeError(f'{values} is an invalid export location. '
                                             f'Example --export-path /a/directory or '
                                             f'--export-path https://<<my_storage_account>>.blob.core.windows.net/'
                                             f'<<my_container>>/')
        setattr(namespace, self.dest, values)


def azure_subscription_id(subscription_id):
    """Setting a type for an subscription id argument."""
    if not is_valid_subscription_id(subscription_id):
        raise ArgumentTypeError(f'Subscription id {subscription_id} provided does not seem to be valid.')
    return subscription_id


def get_mutually_exclusive_args(arg1, arg2, required=False, msg=None):
    """Test if multiple mutually exclusive arguments are provided.

    Args:
        arg1 (Any): First argument to be checked
        arg2 (Any): Second argument to be checked
        required (bool, optional): Wether one argument is required. Defaults to False.
        msg (str, optional): Error message shown to the user. Defaults to None.

    Raises:
        MutuallyExclusiveArguments: If both arguments were provided
        MissingRequiredArguments: If `required` is True and no argument was provided

    Returns:
        arg1 and arg2 after validation

    """
    if arg1 and arg2:
        raise MutuallyExclusiveArguments(arg1, arg2, msg)
    if required and not (arg1 or arg2):
        raise MissingRequiredArguments(msg)
    return arg1, arg2
