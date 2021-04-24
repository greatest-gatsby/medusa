from pyfakefs.fake_filesystem_unittest import TestCase
from pyfakefs import fake_filesystem

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


    # Verifies that the server parser prints help w/o raising if no command is given
    def test_parser_server_noCommand(self):
        args = []

        parser = medusa.parsers.get_server_parsers()

        args_parsed = parser.parse_args(args)
        

        pass

