import yaml


def load_config():
    with open("utils/config.yml", "r") as file:
        config = yaml.safe_load(file)
    return config


def load_config_test():
    with open("app/utils/config.yml", "r") as file:
        config = yaml.safe_load(file)
    return config