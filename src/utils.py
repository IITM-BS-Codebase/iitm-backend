from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_current_user, get_jwt
from flask_jwt_extended.exceptions import NoAuthorizationError

def check_any_role(roles):
    """
    Decorator function that protects routes from being accessed only by specified roles
    Params:
        roles: List[Str] 
        List of roles to be allowed, pass a list of strings with role name
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
    def decorator(f):
        @wraps
        def decorator_function(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            print(claims)
            return f(*args, **kwargs)
        return decorator_function
    return decorator