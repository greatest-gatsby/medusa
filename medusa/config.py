import io
import json
import os

import appdirs

from . import filebases

APP_NAME = 'medusa'
APP_AUTHOR = 'Jay Rode'
CONFIG_NAME = 'medusa.json'

def process_config(args):
    if (args.action == 'get'):
        val = get_config_value(args.property)
        if (val is None):
            print("No key named", args.property)
        else:
            print(val)
    elif (args.action == 'set'):
        set_config_value(args.property, args.value)
    elif (args.action == 'init'):
        init_config(args.path)
    elif (args.action == 'where'):
        print(get_config_location())
    else:
        print('Please specify a subcommand for "config"')

def get_config_value(key):
    try:
        dat = open(get_config_location(), 'r')
        obj = json.load(dat)
        return obj[key]            
    except:
        print("Failure")

def set_config_value(key, value):
    try:
        if not (os.path.getsize(get_config_location())):
            print('Config is empty -- generate a new one with `medusa config init`')
            exit(code=1)
        file = open(get_config_location(), 'r')
        obj = json.load(file)
    except json.JSONDecodeError as jer:
        print('Error opening config for write -- file is malformed or corrupt')
        exit(code=1)
    except:
        print("Unknown error opening config for write")
        raise

    if (key in obj):
        obj[key] = value
        try:
            with open(get_config_location(), 'w') as file:
                json.dump(obj, file)
        except:
            print('Error writing updated config to disk')
    else:
        print('No key named', key)
    

def init_config(path):
    # use given path and default name if given path is a directory
    if (path is str and os.path.isdir(path)):
        file_path = os.path.join(path,CONFIG_NAME)
    elif (path is None or path == ''):
        file_path = ''

    # create directory if not exists
    if not (os.path.isdir(os.path.dirname(get_config_location()))):
        try:
            os.makedirs(os.path.dirname(get_config_location()))
        except:
            print('Error occured while creating config directory')
            return
    
    # open and write
    try:
        with open(get_config_location(), 'w') as file:
            file.write(filebases.DATA)
    except:
        print('Error occured while writing new config')
        return
    
    # print result
    print('Created new Medusa config at', os.path.abspath(get_config_location()))

def get_config_location():
    return "data/medusa.json"
    return os.path.join(
        appdirs.site_config_dir(APP_NAME, APP_AUTHOR),
        'medusa.json'
    )

def get_data_location():
    return "data/medusa-data.json"
    return os.path.join(
        appdirs.site_config_dir(APP_NAME, APP_AUTHOR),
        'medusa-data.json'
    )