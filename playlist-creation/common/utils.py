import yaml
from datetime import datetime, date
import re

def str_to_date(date_val):

    date_output = datetime.strptime(date_val, "%Y-%m-%d")

    return(date_output)

def date_to_str(date_val):

    date_output = date_val.strftime("%Y-%m-%d")

    return(date_output)

def read_yaml(path=None):

    config = None

    with open(path, "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    return(config)

def remove_special_characters(string_value):

    new_string = re.sub("[^A-Za-z0-9]+", "", string_value)

    return(new_string)
