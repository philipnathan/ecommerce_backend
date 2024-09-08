from flask import Blueprint

transactions_blueprint = Blueprint(
    "transactions_blueprint", __name__, url_prefix="/api/transactions"
)

from . import transactions_controller
