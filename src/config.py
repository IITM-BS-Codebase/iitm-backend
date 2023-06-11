import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
"""
Configuration Variables Go Here
"""

class Config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False

class LocalDevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DB_CONNECTION_STRING")
    DEBUG = True
    PASETO_PRIVATE_KEY = os.environ.get("PASETO_PRIVATE_KEY")


MAIN_GUILD_ID = 1104485753758687333
DISCORD_API_ENDPOINT = "https://discord.com/api/v10"
DISCORD_CDN_ENDPOINT = "https://cdn.discordapp.com"