from flask import Blueprint

addresses_blueprint = Blueprint(
    "addresses_blueprint", __name__, url_prefix="/api/addresses"
)

from . import addresses_controller
