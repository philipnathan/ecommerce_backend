from flask import Blueprint

products_blueprint = Blueprint(
    "products_blueprint", __name__, url_prefix="/api/products"
)

from . import products_controller
from . import product_controller_user
