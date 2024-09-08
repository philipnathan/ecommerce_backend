from flask import Blueprint

shipping_options_blueprint = Blueprint(
    "shipping_options_blueprint", __name__, url_prefix="/api/shippingoptions"
)

from . import shipping_options_controller
