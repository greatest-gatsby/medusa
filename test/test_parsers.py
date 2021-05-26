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
        args = ['remove', 'my alias']
        parser = medusa.parsers.get_server_parsers()
        
        args_parsed = parser.parse_args(args)
        assert args_parsed.action == 'remove'
        assert args_parsed.identifier == 'my alias'

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

    def test_parser_server_setAlias(self):
        args = ['set', 'server id', 'alias', 'nickname']
        parser = medusa.parsers.get_server_parsers()

        args_parsed = parser.parse_args(args)
        assert args_parsed.property == 'alias'
        assert args_parsed.identifier == 'server id'
        assert args_parsed.value == 'nickname'

    def test_parser_server_setPath(self):
        args = ['set', 'server id', 'path', '/new/amazing/path']
        parser = medusa.parsers.get_server_parsers()

        args_parsed = parser.parse_args(args)
        assert args_parsed.property == 'path'
        assert args_parsed.identifier == 'server id'
        assert args_parsed.value == '/new/amazing/path'

    def test_parser_server_setType(self):
        args = ['set', 'server id', 'type', 'Paper']
        parser = medusa.parsers.get_server_parsers()

        args_parsed = parser.parse_args(args)
        assert args_parsed.property == 'type'
        assert args_parsed.identifier == 'server id'
        assert args_parsed.value == 'Paper'

    def test_parser_config_get(self):
        args = ['get', 'test-key']
        parser = medusa.parsers.get_config_parsers()

        args_parsed = parser.parse_args(args)
        assert args_parsed.action == 'get'
        assert args_parsed.property == 'test-key'

    def test_parser_config_set(self):
        args = ['set', 'test-key', 'test-value']
        parser = medusa.parsers.get_config_parsers()

        args_parsed = parser.parse_args(args)
        assert args_parsed.action == 'set'
        assert args_parsed.property == 'test-key'
        assert args_parsed.value == 'test-value'

    def test_parser_config_init(self):
        args = ['init']
        parser = medusa.parsers.get_config_parsers()

        args_parsed = parser.parse_args(args)
        assert args_parsed.action == 'init'

    def test_parser_config_where(self):
        args = ['where']
        parser = medusa.parsers.get_config_parsers()

        args_parsed = parser.parse_args(args)
        assert args_parsed.action == 'where'

    def test_parser_verbosity(self):
        args = ['where', '-vvvv', '--verbose']
        parser = medusa.parsers.get_config_parsers()
        
        args_parsed = parser.parse_args(args)
        assert args_parsed.verbose == 5

