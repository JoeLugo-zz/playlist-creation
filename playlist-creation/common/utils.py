import yaml
from datetime import datetime, date

def str_to_date(date_val):

    date_output = datetime.strptime(date_val, "%Y-%m-%d")

    return(date_output)

def date_to_str(date_val):

    date_output = date_val.strftime("%Y-%m-%d")

    return(date_output)

def read_yaml(path=None):
    config = None

    with open(path, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    return(config)
