import os


class Config:
    APP_ID = int(os.environ.get("APP_ID", 0))
    API_HASH = os.environ.get("API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "./downloads")
    TIMEOUT = int(os.environ.get("TIMEOUT", 0))  # time in minute
    MAX_SIZE = int(os.environ.get("MAX_SIZE", 1900000000))
    CUSTOM_THUMB = os.environ.get("CUSTOM_THUMB", None)
    # EDIT_TIME = int(os.environ.get("EDIT_TIME", 0))
