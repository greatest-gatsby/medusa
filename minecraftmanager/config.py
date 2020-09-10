import io
import json
import os

import appdirs

APP_NAME = 'medusa'
APP_AUTHOR = 'Jay Rode'

def process_config(args):
    if (args.action == 'get'):
        get_config_value(args.action)
    elif (args.action == 'set'):
        print('set')
    elif (args.action == 'init'):
        init_config()

def get_config_value(key):
    try:
        dat = open(get_config_location(), 'r')
        obj = json.loads(dat)
        print(obj['save_data'])
    except:
        print("")

def set_config_value(key, value):
    print('')

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