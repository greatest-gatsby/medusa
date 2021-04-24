from pyfakefs.fake_filesystem_unittest import TestCase
from pyfakefs import fake_filesystem

from prettytable import PrettyTable

import json
import unittest
import unittest.mock
import os

import medusa.server

class ServerTestCase(TestCase):

    def setUp(self):
        self.setUpPyfakefs()

    # Verifies that the `server` command invokes the server CLI parser
    @unittest.mock.patch('medusa.parsers.get_server_parsers')
    def test_server_process_callsParser(self, mock_parser_getter):
        args = []
        mock_parser = unittest.mock.Mock()
        mock_parser_getter.return_value = mock_parser

        medusa.server.process_server(args)

        mock_parser_getter.assert_called_once()
        mock_parser.parse_args.assert_called_once()


    # Verifies that the list function shows a message when there are no registered servers
    @unittest.mock.patch('builtins.print')
    @unittest.mock.patch('medusa.server._servers', return_value = [])
    def test_server_list_printsWhenEmpty(self, mock_servers, mock_print):
        medusa.server.list_servers()

        mock_print.assert_called_once_with('No registered servers')

    # Verifies that the list function accesses and prints key server fields
    @unittest.mock.patch('medusa.server._servers')
    @unittest.mock.patch('builtins.print')
    def test_server_list_accessesFields(self, mock_print, mock_servers):
        srv1 = medusa.server.Server()
        srv1.Alias = 'Friendly'
        srv1.Path = '/Test1'
        srv1.Type = medusa.server.ServerType.PAPER

        medusa.server._servers = [srv1]
        medusa.server.list_servers()

        assert 'No registered servers' not in mock_print.call_args.args

        table = mock_print.call_args.args[0]

        assert 'Friendly' in table.get_string(fields=['Alias'])
        assert 'Test1' in table.get_string(fields=['Path'])
        assert 'PAPER' in table.get_string(fields=['Type'])


        pass

