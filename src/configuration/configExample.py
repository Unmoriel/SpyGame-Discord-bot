from json import load
from os import path

"""
THIS FILE SHOULD BE NAMED config.py 
"""

CHEMIN = path.abspath(path.split(__file__)[0]) + "/"

config_code = {
    "discord": "",
    "riot": "",
    "bdd": {
        "host": "",
        "user": "",
        "password": "",
        "database": "",
    },
    "cloudinary": {
        "cloud_name": "",
        "api_key": "",
        "api_secret": ""
    }
}


def get_conf() -> dict:
    """Get the configuration, either from the file conf.json or from this file."""
    return get_conf_file()  # Change this line to get_conf_code() to use the configuration from this file


def get_riot_key() -> str:
    """Get the Riot API key from the configuration file."""
    return get_conf()['riot']


def get_discord_key() -> str:
    """Get the Discord API key from the configuration file."""
    return get_conf()['discord']


def get_cloudinary_key() -> str:
    """Get the Cloudinary API key from the configuration file."""
    return get_conf()['cloudinary']


def get_bdd_conf() -> dict:
    return get_conf()['bdd']


def get_conf_code() -> dict:
    """Get the configuration for the database from this file."""
    return config_code


def get_conf_file() -> dict:
    """Get the configuration for the database from the file conf.json."""
    with open(CHEMIN + "conf.json", 'r') as f:
        return load(f)
