import requests
import os
from flask import Blueprint, redirect, request
from flask_jwt_extended import create_access_token

from src.config import *
from src.models import DiscordOAuth, User
from src.database import db

discord_bp = Blueprint("discord_bp", __name__, url_prefix='/discord/auth')


@discord_bp.route("/login")
def login():
    """
    Redirect to discord auth
    """
    return redirect(os.environ.get("DISCORD_OAUTH_URL"))


@discord_bp.route("/login/callback")
def callback():
    """
    Returned from discord after oauth
    """
    token_access_code = request.args.get("code", None)
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
            print("created user", user)
            user_oauth = DiscordOAuth(oauth_data, user.id)
        else:
            #user exists, update oauth
            user_oauth = DiscordOAuth.query.filter(DiscordOAuth.user_id == user.id).first() 
            user_oauth.update_oauth(oauth_data)

        token = create_access_token(identity=user.id, additional_claims={
                                    'roles': user.get_roles()})

        db.session.add(user)
        db.session.add(user_oauth)
        db.session.flush()
        db.session.commit()

        return {"Token": token}

    return redirect(os.environ.get("FRONTEND_URL"))
