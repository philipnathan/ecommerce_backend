from flask import request
from flasgger import swag_from

from . import products_blueprint
from .products_services import ProductsServices
from .product_services_user import ProductServicesUser

service = ProductsServices()
user_service = ProductServicesUser()


@products_blueprint.route("/user/product/<int:product_id>", methods=["GET"])
@swag_from("./products_user_get_product.yml")
def get_product_by_id(product_id):
    return service.get_product_by_id(product_id, "user")


@products_blueprint.route("/user/query", methods=["GET"])
@swag_from("./products_user_get_by_filter.yml")
def get_product_by_filter():
    req = request
    return user_service.get_product_by_filter(req)
