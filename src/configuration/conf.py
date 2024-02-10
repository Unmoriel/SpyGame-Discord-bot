from json import load
from os import path
CHEMIN = path.abspath(path.split(__file__)[0]) + "/"


conf_code = {}


def get_conf() -> dict:
    """Get the configuration for the database from this file."""
    return get_conf_file()


def get_riot_key() -> str:
    """Get the Riot API key from the configuration file."""
    return get_conf_file()['riot']


def get_discord_key() -> str:
    """Get the Discord API key from the configuration file."""
    return get_conf_file()['discord']


def get_cloudinary_key() -> str:
    """Get the Cloudinary API key from the configuration file."""
    return get_conf_file()['cloudinary']


def get_conf_code() -> dict:
    """Get the configuration for the database from this file."""
    return conf_code


def get_conf_file() -> dict:
    """Get the configuration for the database from the file conf.json."""
    with open(CHEMIN + "conf.json", 'r') as f:
        return load(f)


