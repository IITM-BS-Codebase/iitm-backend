from flask import Blueprint

from src.utils import check_any_role, check_discord_auth

basic_bp = Blueprint("basic_bp",__name__,url_prefix="/basic")

@basic_bp.route("/ping")
def ping():
    return "Pong!", 200

@basic_bp.route("/admin")
@check_any_role(roles=['Admin'])
def admin():
    return "Admin Endpoint Verified", 200

@basic_bp.route("/discord")
@check_discord_auth()
def discord():
    return "Discord Endpoint Verified", 200

