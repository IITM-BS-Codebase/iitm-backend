from datetime import timedelta
import config


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
    SQLALCHEMY_DATABASE_URI = config.postgresql
    DEBUG = True
    PASETO_PRIVATE_KEY = config.paseto_private_key


MAIN_GUILD_ID = 1104485753758687333
DISCORD_API_ENDPOINT = "https://discord.com/api/v10"
DISCORD_CDN_ENDPOINT = "https://cdn.discordapp.com"