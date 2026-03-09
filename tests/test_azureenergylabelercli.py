#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: test_azureenergylabelercli.py
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
test_azureenergylabelercli
----------------------------------
Tests for `azureenergylabelercli` module.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import json
import sys
import unittest
from unittest.mock import patch

from azureenergylabelercli.azureenergylabelercli import get_arguments
from azureenergylabelercli.azureenergylabelercliexceptions import MissingRequiredArguments

__author__ = '''Sayantan Khanra <skhanra@schubergphilis.com>'''
__docformat__ = '''google'''
__date__ = '''04-05-2022'''
__copyright__ = '''Copyright 2022, Sayantan Khanra'''
__credits__ = ["Sayantan Khanra"]
__license__ = '''MIT'''
__maintainer__ = '''Sayantan Khanra'''
__email__ = '''<skhanra@schubergphilis.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".


class TestGetArguments(unittest.TestCase):

    def test_minimal_arguments(self):
        """Test that providing only --tenant-id produces valid args."""
        test_args = ['prog', '--tenant-id', '00000000-0000-0000-0000-000000000000']
        with patch.object(sys, 'argv', test_args):
            args = get_arguments()
        self.assertEqual(args.tenant_id, '00000000-0000-0000-0000-000000000000')
        self.assertEqual(args.log_level, 'info')
        self.assertFalse(args.to_json)
        self.assertTrue(args.export_all)

    def test_missing_tenant_id_raises(self):
        """Test that missing --tenant-id raises MissingRequiredArguments."""
        test_args = ['prog']
        with patch.object(sys, 'argv', test_args):
            with self.assertRaises(MissingRequiredArguments):
                get_arguments()

    def test_frameworks_parsed_as_list(self):
        """Test that comma-delimited frameworks are parsed into a list."""
        test_args = ['prog', '--tenant-id', '00000000-0000-0000-0000-000000000000',
                     '--frameworks', 'Microsoft cloud security benchmark,Azure CIS 1.1.0']
        with patch.object(sys, 'argv', test_args):
            args = get_arguments()
        self.assertEqual(args.frameworks, ['Microsoft cloud security benchmark', 'Azure CIS 1.1.0'])