from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from src.config import LocalDevelopmentConfig
from src.database import db
from src.models import *

def create_app(): 
    """
    Create flask app and setup default configuration
    """
    app = Flask(__name__)
    CORS(app)

    #change this in prod
    app.config.from_object(LocalDevelopmentConfig)

    db.init_app(app)

    api = Api(app)
    with app.app_context():
        db.create_all()


    return app, api


def setup_routes(app):
    """
    Register blueprints and any API resources
    """

    from .routes.auth.discord import discord_bp
    from .routes.auth.google import google_bp
    from .routes.basic import basic_bp
    
    app.register_blueprint(discord_bp)
    app.register_blueprint(basic_bp)
    app.register_blueprint(google_bp)
