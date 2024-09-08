from flask import Blueprint

calculators_blueprint = Blueprint(
    "calculators_blueprint", __name__, url_prefix="/api/calculators"
)

from . import calculators_controller
