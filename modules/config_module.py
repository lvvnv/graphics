import ast

# todo: add colorspaces to cfg file

class ConfigParser:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = {}

    def read_config(self):
        fin = open(self.config_path, "r")
        with fin:
            keyval = fin.readline().rstrip()
            key, value = keyval.split('=')
            value = [x.strip() for x in ast.literal_eval(value)]
            self.config[key] = value
