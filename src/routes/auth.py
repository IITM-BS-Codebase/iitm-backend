import requests
import os
from flask import Blueprint, redirect, request
from flask_jwt_extended import current_user, create_access_token

from ..config import *
from ..models import DiscordOAuth, User


discord_bp = Blueprint("auth_bp",__name__, url_prefix='/discord/auth')

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

    token_access_code = request.args.get("code",None)
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

        user = User(r.json(), DiscordOAuth(oauth_data))
        token = create_access_token(identity=user.id, additional_claims={
                                    'roles': user.get_roles(),**user.discord_oauth.__dict__()})

        return {"Token":token}
 



    return redirect(os.environ.get("FRONTEND_URL"))

