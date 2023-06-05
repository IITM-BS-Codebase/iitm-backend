from functools import wraps
from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_current_user
from flask_jwt_extended.exceptions import NoAuthorizationError

from .config import LocalDevelopmentConfig
from .database import db
from .validation import BusinessValidationError
from .models import User

def create_app(): 

    app = Flask(__name__)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    bcrypt = Bcrypt(app)
    app.config.from_object(LocalDevelopmentConfig)

    db.init_app(app)

    api = Api(app)
    with app.app_context():
        db.create_all()

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.log_exception(e)
        return BusinessValidationError(error_code=400, error_message=e.message)

    return app, api

def setup_auth(app):

    jwt = JWTManager(app)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """ callback for fetching authenticated user from db """
        print("IN user lookup loader")
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).one_or_none()


def setup_routes(api):

    # from .api.auth import LoginAPI, SignupAPI
    # from .api.home import Home, AdminHome

    # api.add_resource(LoginAPI,"/api/login")
    # api.add_resource(SignupAPI,"/api/signup")
    # api.add_resource(Home, "/api/home")
    # api.add_resource(AdminHome, "/api/admin")
    pass

def check_any_role(roles):
    def decorator(f):
        @wraps(f)
        def decorator_function(*args, **kwargs):
            # calling @jwt_required()
            verify_jwt_in_request()
            # fetching current user from db
            current_user = get_current_user()
            # checking user role
            if not set(current_user.get_roles()).intersection(roles):
                raise NoAuthorizationError("Role is not allowed.")
            return f(*args, **kwargs)
        return decorator_function
    return decorator
