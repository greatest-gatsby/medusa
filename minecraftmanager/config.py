import io
import json
import os

import appdirs

APP_NAME = 'medusa'
APP_AUTHOR = 'Jay Rode'

def process_config(args):
    if (args.action == 'get'):
        get_config_value(args.property)
    elif (args.action == 'set'):
        set_config_value(args.property, args.value)
    elif (args.action == 'init'):
        init_config()
    elif (args.action == 'where'):
        print(get_config_location())
    else:
        print('Please specify a subcommand for "config"')

def get_config_value(key):
    try:
        dat = open(get_config_location(), 'r')
        obj = json.load(dat)
        if (key in obj):
            print(obj[key])
        else:
            print("No key named", key)
    except:
        print("Failure")

def set_config_value(key, value):
    try:
        obj = json.load(open(get_config_location(), 'r'))
    except:
        print('Error opening config for write')

    if (key in obj):
        obj[key] = value
        try:
            with open(get_config_location(), 'w') as file:
                json.dump(obj, file)
        except:
            print('Error writing updated config to disk')
    else:
        print('No key named', key)
    

def init_config():
    # create directory if not exists
    if not (os.path.isdir(os.path.dirname(get_config_location()))):
        try:
            os.makedirs(os.path.dirname(get_config_location()))
        except:
            print('Error occured while creating config directory')
            return
    
    # open and read
    try:
        with open('data/medusa.json', 'r') as file:
            new_data = file.readlines()
            # open and write
            with open(get_config_location(), 'w') as target:
                target.writelines(new_data)
    except:
        print('Error occured while writing new config')
        return
    
    # print result
    print('Created new Medusa config at', get_config_location())

def get_config_location():
    return os.path.join(appdirs.site_config_dir(APP_NAME, APP_AUTHOR), 'medusa.json')