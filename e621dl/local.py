import os
from datetime import date
import yaml
from e621dl import constants

def make_config():
    with open('config.yaml', 'wt', encoding = 'utf-8') as file:
        file.write(constants.DEFAULT_CONFIG_TEXT)
        print('[i] New default config file created. Please add tag groups to this file.')
    raise SystemExit

def get_config():
    if not os.path.isfile('config.yaml'):
        print('[!] No config file found.')
        make_config()

    with open('config.yaml', 'rt', encoding = 'utf-8') as file:
        return yaml.load(file, Loader = yaml.SafeLoader)
   
def get_start_date(days_to_check):
    return date.fromordinal(max(date.today().toordinal() - (days_to_check - 1), 1)).strftime('%Y-%m-%d')

def substitute_illegal_chars(char):
    return '_' if char in ['\\', ':', '*', '?', '\"', '<', '>', '|', ' '] else char

def make_path(dir_name, filename, ext):
    clean_dir_name = ''.join([substitute_illegal_chars(char) for char in dir_name])

    if not os.path.isdir(f"downloads/{clean_dir_name}"):
        os.makedirs(f"downloads/{clean_dir_name}")

    return f"downloads/{clean_dir_name}/{filename}.{ext}"
