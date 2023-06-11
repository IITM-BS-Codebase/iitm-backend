from __future__ import annotations
import json
import os

import time
from functools import wraps
from typing import TYPE_CHECKING, Any
from flask import Request, request
from paseto.v4 import PublicKey, Ed25519PrivateKey
import paseto
from werkzeug.exceptions import Unauthorized

class NoAuthorizationError(Unauthorized):
    ...


if TYPE_CHECKING:
    from src.models import DiscordOAuth, User

def decode_key(key_hex: str) -> PublicKey:
    secret = bytes.fromhex(key_hex)
    return PublicKey(Ed25519PrivateKey.from_private_bytes(secret))


def sign(payload: dict[str, Any], expires: int = 900) -> str:
    key = decode_key(os.environ['PASETO_PRIVATE_KEY'])
    signature = paseto.encode(key, payload, exp=expires)
    return signature.decode('ascii')


def verify(token: str) -> dict[str, Any] | None:
    if not token:
        return None
    public = decode_key(os.environ['PASETO_PRIVATE_KEY'])
    try:
        ret = paseto.decode(public, token, deserializer=json)
    except paseto.VerificationError:
        return None
    return ret.payload


def get_nonce_from_cookie(cookie: str | None) -> str | None:
    if cookie is None:
        return None
    target = None
    for part in cookie.split('; '):
        if part.startswith('nonce='):
            target = part
            break
    if target is None:
        return None
    _, _, value = target.partition('=')
    return value


def validate_request_state(state: str, request: Request) -> dict[str, Any] | None:
    nonce = get_nonce_from_cookie(request.headers.get('Cookie'))
    if nonce is None:
        return None
    payload = verify(state)
    if payload is None:
        return None
    if payload['nonce'] != nonce:
        return None
    return payload


def get_current_user() -> User | None:
    payload = validate_request_state(request.args.get('state', ''), request)
    if payload is None:
        return None
    return User.query.filter_by(id=int(payload['sub'])).one_or_none()


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
            # fetching current user from db
            current_user = get_current_user()
            if current_user is None:
                raise NoAuthorizationError("User is not authenticated.")
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
            payload = validate_request_state(request.args.get('state', ''), request)
            if payload is None:
                raise NoAuthorizationError("Invalid state!")
            sub = payload['sub']
            discord_oauth = DiscordOAuth.query.filter(DiscordOAuth.user_id == sub).one_or_none()
            if not discord_oauth:
                raise NoAuthorizationError("DiscordOAuth is not present!")
            if time.time() > discord_oauth.valid_until:
                raise NoAuthorizationError("DiscordOAuth has expired!")
            return f(*args, **kwargs)
        return decorator_function
    return decorator
