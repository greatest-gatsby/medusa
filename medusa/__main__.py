import argparse
import os
import subprocess
import sys
import inspect

# Medusa imports
import medusa.config
import medusa.parsers
import medusa.run
import medusa.server

# init submodules
# servers = server.get_servers_from_config()


if __name__ == '__main__':

    # inspect command, then handle in the respective submodule
    # pop the subcommand from argv because argparse will be used
    # on argv and is only expecting the command options, we are triggering the command itself

    if len(sys.argv) < 2:
        cmd = ""
    else:
        cmd = sys.argv[1]
        args = sys.argv[2:]
    
    if (cmd == 'config'):
        config.process_config(args)
    elif (cmd == 'status'):
        status.process_status(args)
    elif (cmd == 'server'):
        server.process_server(args)
    elif (cmd == 'run'):
        run.process_run(args)
    else:
        print("HELP HERE")