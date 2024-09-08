from flask import Blueprint

shipments_blueprint = Blueprint(
    "shipments_blueprint", __name__, url_prefix="/api/shipments"
)

from . import shipments_controller
