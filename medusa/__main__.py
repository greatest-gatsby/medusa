import argparse
import os
import subprocess
import sys
import inspect

# Medusa imports
from . import config
from . import parsers
from . import server
from . import status

# init submodules
servers = server.get_servers_from_config()


if __name__ == '__main__':

    # inspect command, then handle in the respective submodule
    # pop the subcommand from argv because argparse will be used
    # on argv and is only expecting the command options, we are triggering the command itself

    if len(sys.argv) < 2:
        cmd = ""
    else:
        cmd = sys.argv[1]
        #print(sys.argv)
        sys.argv = sys.argv[2:]
        #print(sys.argv)
    
    
    if (cmd == 'config'):
        config.process_config(sys.argv)
    elif (cmd == 'status'):
        status.process_status(args)
    elif (cmd == 'server'):
        server.process_server(sys.argv, servers)
    else:
        print("HELP HERE")