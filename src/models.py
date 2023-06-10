import requests
import time
from flask_login import UserMixin, AnonymousUserMixin
from flask_jwt_extended import verify_jwt_in_request, get_jwt, current_user
from .database import db
from .config import *


users_roles = db.Table(
    'users_roles',
    db.Column('user_id', db.BigInteger, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class DiscordOAuth(db.Model):
    """
    Class to represent user's OAuth data.
    """
    __tablename__ = 'discord_oauth'
    user_id = db.Column(db.BigInteger,db.ForeignKey('user.id'),primary_key=True, )
    access_token = db.Column(db.String(100), unique=True)
    refresh_token = db.Column(db.String(100), unique=True)
    valid_until = db.Column(db.BigInteger)
    token_type = db.Column(db.String(50))
    scope = db.Column(db.String(200))

    def __init__(self,data: dict, user_id: int) -> None:
        self.user_id = user_id
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        self.valid_until = time.time() + int(data["expires_in"])
        self.token_type = data["token_type"]
        self.scope = data["scope"]

    def update_oauth(self, data: dict):
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        self.valid_until = time.time() + int(data["expires_in"])
        self.token_type = data["token_type"]
        self.scope = data["scope"]

    def to_dict(self):
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "valid_until": self.valid_until,
            "token_type": self.token_type,
            "scope": self.scope,
        }


class Role(db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key =True, autoincrement=True)
    name = db.Column(db.String(50), unique=True)

    def __init__(self, name=name):
        self.name = name

    def __repr__(self,):
        return f"{self.id}"

class User(UserMixin, db.Model):

    __tablename__ = "user"
    id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    discriminator = db.Column(db.Integer)
    avatar = db.Column(db.String(100))
    roles = db.relationship(
        'Role',
        secondary=users_roles,
        backref=db.backref('users',lazy='dynamic')
        )
    discord_oauth = db.relationship('DiscordOAuth',backref=db.backref('user'),uselist=False)

    def __repr__(self):
        return f"{self.id}"

    def __init__(self, data: dict,roles=[]) -> None:
        self.id = data["id"]
        self.username = data["username"]
        self.discriminator = data["discriminator"]
        #handle default avatars
        if data["avatar"]:
            self.avatar = (
                f"{DISCORD_CDN_ENDPOINT}/avatars/{data['id']}/{data['avatar']}"
            )
        else:
            self.avatar = "https://cdn.discordapp.com/embed/avatars/4.png"

        for role in roles:
            if to_add := Role.query.filter(Role.name == role).first():
                self.add_role(to_add)

    def add_role(self, role):
        self.roles.append(role) 

    def get_roles(self):
        return [role.name for role in self.roles]


    @classmethod
    def authenticate(cls):
        """
        Function to get discord user from request.
        """

        if verify_jwt_in_request():
            data = get_jwt() 
            return User.get_from_token(DiscordOAuth(data))

        if not isinstance(current_user, AnonymousUserMixin) and current_user:
            return current_user
        else:
            raise Exception("No user logged in")

    @classmethod
    def get_from_token(cls, oauth_data: DiscordOAuth) -> "User":
        """
        Get user from discord access token.
        (For member)
        """
        url = f"{DISCORD_API_ENDPOINT}/users/@me"

        headers = {"Authorization": f"Bearer {oauth_data.access_token}"}

        response = requests.request("GET", url, headers=headers)
        response = response.json()
        return cls(response)


    def to_dict(self) -> dict:
        res = {
            "id": self.id,
            "username": self.username,
            "discriminator": self.discriminator,
            "avatar": self.avatar,
            "mfa_enabled": self.mfa_enabled,
        }
        return res
    