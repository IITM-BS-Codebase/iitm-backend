from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

from src.config import LocalDevelopmentConfig
from src.database import db
from src.models import User

def create_app(): 
    """
    Create flask app and setup default configuration
    """
    app = Flask(__name__)
    cors = CORS(app)
    bcrypt = Bcrypt(app)

    #change this in prod
    app.config.from_object(LocalDevelopmentConfig)

    db.init_app(app)

    api = Api(app)
    with app.app_context():
        db.create_all()


    return app, api

def setup_auth(app):
    """
    Setup JWT authentication
    """

    jwt = JWTManager(app)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """ callback for fetching authenticated user from db """
        identity = jwt_data["sub"]
        return User.query.filter_by(id=int(identity)).one_or_none()


def setup_routes(app):
    """
    Register blueprints and any API resources
    """

    from .routes.auth import discord_bp
    from .routes.basic import basic_bp
    
    app.register_blueprint(discord_bp)
    app.register_blueprint(basic_bp)

