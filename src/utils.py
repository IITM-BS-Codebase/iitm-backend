import time
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_current_user, get_jwt
from flask_jwt_extended.exceptions import NoAuthorizationError

from src.models import DiscordOAuth

def check_any_role(roles):
    """
    Decorator function that protects routes from being accessed only by specified roles (Internal roles not discord roles!!)
    Params:
        roles: List[Str] 
        List of roles to be allowed, pass a list of role names
    """
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

def check_discord_auth():
    """
    Decorator to verify wether user accessing an endpoint has valid discord oauth
    """
    def decorator(f):
        @wraps(f)
        def decorator_function(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            discord_oauth = DiscordOAuth.query.filter(DiscordOAuth.user_id == claims['sub']).one_or_none()
            if not discord_oauth:
                raise NoAuthorizationError("DiscordOAuth is not present!")
            if time.time() > discord_oauth.valid_until:
                raise NoAuthorizationError("DiscordOAuth has expired!")
            return f(*args, **kwargs)
        return decorator_function
    return decorator