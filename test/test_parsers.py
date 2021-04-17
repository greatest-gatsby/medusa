import argparse
from pyfakefs.fake_filesystem_unittest import TestCase
from pyfakefs import fake_filesystem

import json
import unittest
import unittest.mock
import os

import medusa.parsers

class ParsersTestCase(TestCase):

    def setUp(self):
        self.setUpPyfakefs()

    # Verifies that the server parser accepts the `create` subcommand
    # with a path and optional arguments
    def test_parser_server_create_opts(self):
        args = ['create', 'a path', '-a', 'Alias Maximus', '-t', 'forge']
        parser = medusa.parsers.get_server_parsers()

        args_parsed = parser.parse_args(args)
        assert args_parsed.action == 'create'
        assert args_parsed.path == 'a path'
        assert args_parsed.alias == 'Alias Maximus'
        assert args_parsed.type == 'forge'

    def test_parser_server_remove(self):
        args = ['remove']
        parser = medusa.parsers.get_server_parsers()
        
        args_parsed = parser.parse_args(args)
        assert args_parsed.action == 'remove'

    def test_parser_server_list(self):
        args = ['list']
        parser = medusa.parsers.get_server_parsers()
        
        args_parsed = parser.parse_args(args)
        assert args_parsed.action == 'list'

    def test_parser_server_scan(self):
        args = ['scan']
        parser = medusa.parsers.get_server_parsers()
        
        args_parsed = parser.parse_args(args)
        assert args_parsed.action == 'scan'
