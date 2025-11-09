import os

import toml
from dotenv import load_dotenv

from .sqllite import DatabaseFunctions as dbf


def load_env(env: str):
    """Load environment vars"""

    if env:
        # Expand user path and normalize the path
        ENV_PATH = os.path.expanduser(env)
        # Remove any extra quotes that might have been passed
        ENV_PATH = ENV_PATH.strip('"').strip("'")
    else:
        loaded_env = dbf.select_env()
        ENV_PATH = loaded_env or ".env"

    try:
        dbf.update_env(ENV_PATH)
        if os.path.exists(ENV_PATH):
            load_dotenv(ENV_PATH)
        elif ENV_PATH != ".env":  # Only warn if a specific path was provided
            print(f"Warning: Environment file not found: {ENV_PATH}")
    except FileNotFoundError:
        print(f"Couldn't find file: {ENV_PATH}")
    except Exception as e:
        print(f"Error loading environment variables: {e}")


def load_toml(conf_path: str):
    """Try to load config"""

    if not conf_path:
        if conf := dbf.select_config():
            conf_path = conf
            dbf.update_config(conf_path)
        else:
            config_dir = dbf.get_config_dir()
            conf_path = str(config_dir / "conf.toml")
            dbf.update_config(conf_path)
    else:
        # Expand user path and normalize the path
        conf_path = os.path.expanduser(conf_path)
        # Remove any extra quotes that might have been passed
        conf_path = conf_path.strip('"').strip("'")

    try:
        if not os.path.exists(conf_path):
            raise FileNotFoundError(f"Config file not found: {conf_path}")
        with open(conf_path, "r", encoding="utf-8") as t:
            return toml.load(t)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        raise
    except toml.TomlDecodeError as e:
        error_msg = str(e)
        if "escape sequence" in error_msg.lower():
            print(f"Error: Invalid TOML format in config file '{conf_path}': {e}")
            print("\nWindows path issue detected!")
            print("In TOML files, backslashes in double-quoted strings are escape sequences.")
            print("To fix this, use one of the following options:")
            print("  1. Use single quotes (literal strings): path = 'C:\\Users\\...'")
            print("  2. Escape backslashes: path = \"C:\\\\Users\\\\...\"")
            print("  3. Use forward slashes (works on Windows): path = \"C:/Users/...\"")
            print("\nExample:")
            print("  [wiki]")
            print("  path = \"C:/Users/simni/OneDrive/Bureau/notes\"")
            print("  # or")
            print("  path = 'C:\\Users\\simni\\OneDrive\\Bureau\\notes'")
        else:
            print(f"Error: Invalid TOML format in config file '{conf_path}': {e}")
        raise
    except Exception as e:
        print(f"Error loading config file '{conf_path}': {e}")
        raise
