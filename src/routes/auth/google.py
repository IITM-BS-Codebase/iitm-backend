import os
import secrets
from urllib.parse import urlencode
from flask import Blueprint, Response, request
import requests
from src.utils import validate_request_state, sign, verify
google_bp = Blueprint("google_bp", __name__, url_prefix='/google/auth')

GOOGLE_OPENID_ENDPOINT = "https://accounts.google.com/.well-known/openid-configuration"


@google_bp.route("/login")
def login():
    
    google_provider_config = requests.get(GOOGLE_OPENID_ENDPOINT).json()
    auth_endpoint = google_provider_config["authorization_endpoint"]
    redirect_uri = request.base_url + "/callback"
    headers = {}
    payload = validate_request_state(request.args.get('state', ''), request)
    if payload is None:
        nonce = secrets.token_urlsafe(32)
        cookie = f'nonce={nonce}; SameSite=Lax; Secure; HttpOnly; Max-Age=90000; Path=/'
        headers['Set-Cookie'] = cookie
        payload = {'nonce': nonce}
    scope = 'openid email profile'
    params = {
        'client_id': os.environ.get("GOOGLE_CLIENT_ID"),
        'redirect_uri': redirect_uri,
        'scope': scope,
        'response_type': 'code',
        'state': sign(payload)
    }
    headers['Location'] = f'{auth_endpoint}?{urlencode(params)}'
    return Response(status=302, headers=headers)

@google_bp.route("/login/callback")
def callback():
    google_provider_config = requests.get(GOOGLE_OPENID_ENDPOINT).json()  # yeah, we call this twice every flow. But there is absolutely no ratelimit on this.
    code = request.args.get("code", None)
    state = request.args.get("state", None)
    if code is None or state is None:
        return 'missing code or state',400
    validated = validate_request_state(state, request)
    if validated is None:
        return "invalid state",400
    token_endpoint = google_provider_config["token_endpoint"]
    userinfo_endpoint = google_provider_config["userinfo_endpoint"]
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'code': code,
        'client_id': os.environ.get("GOOGLE_CLIENT_ID"),
        'client_secret': os.environ.get("GOOGLE_CLIENT_SECRET"),
        'redirect_uri': request.base_url,
        'grant_type': 'authorization_code'
    }
    token = requests.post(token_endpoint, data=data, headers=headers).json()
    headers = {'Authorization': f'Bearer {token["access_token"]}', 'Accept': 'application/json'}
    user_resp = requests.get(userinfo_endpoint, headers=headers).json()
    validated['email'] = user_resp['email']
    signed = sign(validated)
    return {'Token': signed}
