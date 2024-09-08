from flask import Blueprint

locations_blueprint = Blueprint(
    "locations_blueprint", __name__, url_prefix="/api/locations"
)

from . import locations_controller
