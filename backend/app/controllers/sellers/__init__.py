from flask import Blueprint

sellers_blueprint = Blueprint("sellers_blueprint", __name__, url_prefix="/api/sellers")

from . import sellers_contoller
