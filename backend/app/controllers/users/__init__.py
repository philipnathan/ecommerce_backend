from flask import Blueprint

users_blueprint = Blueprint("users_blueprint", __name__, url_prefix="/api/users")

from . import users_controller
