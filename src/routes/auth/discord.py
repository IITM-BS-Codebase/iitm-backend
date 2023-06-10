import requests
import os
import secrets
from urllib.parse import urlencode
from flask import Blueprint, Response, redirect, request, make_response
from flask_bcrypt import generate_password_hash, check_password_hash

from src.config import *
from src.models import DiscordOAuth, User
from src.database import db
from src.utils import sign, validate_request_state

discord_bp = Blueprint("discord_bp", __name__, url_prefix='/discord/auth')

@discord_bp.route("/login")
def login():
    """
    Redirect to discord auth
    """
    nonce = secrets.token_urlsafe(32)
    state_param = urlencode({
        "state": sign({'nonce': nonce})
    })

    redirect_url = os.environ["DISCORD_OAUTH_URL"] + f"&{state_param}"
    cookie = f'nonce={nonce}; SameSite=Lax; Secure; HttpOnly; Max-Age=90000; Path=/'
    return Response(status=302, headers={'Location': redirect_url, 'Set-Cookie': cookie})


@discord_bp.route("/login/callback")
def callback():
    """
    Returned from discord after oauth
    """
    token_access_code = request.args.get("code", None)
    state_hash = request.args.get("state")
    if token_access_code is None or state_hash is None:
        return 'missing code or state',400
    validated = validate_request_state(state_hash, request)
    if validated is None:
        return "invalid state",400

    data = {
        "client_id": os.environ.get("DISCORD_CLIENT_ID"),
        "client_secret": os.environ.get("DISCORD_CLIENT_SECRET"),
        "grant_type": "authorization_code",
        "code": token_access_code,
        "redirect_uri": os.environ.get("DISCORD_OAUTH_REDIRECT"),
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    r = requests.post(
        f"{DISCORD_API_ENDPOINT}/oauth2/token", data=data, headers=headers
    )

    oauth_data = r.json()

    if "access_token" in oauth_data and "token_type" in oauth_data:
        r = requests.get(
            f"{DISCORD_API_ENDPOINT}/users/@me",
            headers={
                "Authorization": f"{oauth_data['token_type']} {oauth_data['access_token']}"
            },
        )

        user = User.query.filter(User.id == r.json()['id']).one_or_none()
        if not user:
            #user does not exist create entry in db
            user = User(r.json())
            user_oauth = DiscordOAuth(oauth_data, user.id)
        else:
            #user exists, update oauth
            user_oauth = DiscordOAuth.query.filter(DiscordOAuth.user_id == user.id).first() 
            user_oauth.update_oauth(oauth_data)

        validated['sub'] = user.id
        validated['roles'] = user.get_roles()
        signed = sign(validated)

        db.session.add(user)
        db.session.add(user_oauth)
        db.session.flush()
        db.session.commit()

        return {"Token": signed}

    return redirect(os.environ["FRONTEND_URL"])
