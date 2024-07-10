import os
from dotenv import set_key, load_dotenv
from .constants import ANTHROPIC_API_KEY, PROVIDER, MODEL


def save_settings(app, api_key, provider, model):
    os.makedirs(os.path.dirname(env_file()), exist_ok=True)
    set_key(env_file(), ANTHROPIC_API_KEY, api_key)
    set_key(env_file(), PROVIDER, provider)
    set_key(env_file(), MODEL, model)
    app.main_window.info_dialog("Info", "Settings Saved")


def get_api_key():
    return load_env_file()[ANTHROPIC_API_KEY]


def get_provider():
    return load_env_file()[PROVIDER]


def get_model():
    return load_env_file()[MODEL]


def load_env_file():
    load_dotenv(env_file())  # Parse a .env file and then load all the variables found as environment variables.
    return {
        ANTHROPIC_API_KEY: os.getenv(ANTHROPIC_API_KEY),
        PROVIDER: os.getenv(PROVIDER),
        MODEL: os.getenv(MODEL)
    }


def env_file():
    return os.path.expanduser("~/.mentat/.env")
