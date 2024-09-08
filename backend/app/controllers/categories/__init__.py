from flask import Blueprint

categories_blueprint = Blueprint(
    "categories_blueprint", __name__, url_prefix="/api/categories"
)

from . import categories_controller
