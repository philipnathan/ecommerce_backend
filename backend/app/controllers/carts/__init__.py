from flask import Blueprint

carts_blueprint = Blueprint("carts_blueprint", __name__, url_prefix="/api/carts")

from . import carts_controller
