from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from

from . import products_blueprint
from .products_services import ProductsServices


service = ProductsServices()


@products_blueprint.route("/seller/create", methods=["POST"])
@jwt_required()
@swag_from("./products_seller_create.yml")
def product_create():
    data = request.get_json()
    role = get_jwt_identity().get("role")
    role_id = get_jwt_identity().get("id")
    return service.create_product(data, role, role_id)


@products_blueprint.route("/seller", methods=["GET"])
@jwt_required()
@swag_from("./products_seller_get_list.yml")
def product_list():
    role = get_jwt_identity().get("role")
    role_id = get_jwt_identity().get("id")
    req = request
    return service.get_list_products(req, role, role_id)


@products_blueprint.route("/seller/<int:product_id>", methods=["GET"])
@jwt_required()
@swag_from("./products_seller_get_product.yml")
def product_detail(product_id):
    role = get_jwt_identity().get("role")
    role_id = get_jwt_identity().get("id")
    return service.get_product_by_id(product_id, role, role_id)


@products_blueprint.route("/seller/<int:product_id>", methods=["PUT"])
@jwt_required()
@swag_from("./products_seller_update.yml")
def product_update(product_id):
    data = request.get_json()
    role = get_jwt_identity().get("role")
    role_id = get_jwt_identity().get("id")
    return service.update_product(product_id, role, role_id, data)


@products_blueprint.route("/seller/<int:product_id>", methods=["DELETE"])
@jwt_required()
@swag_from("./products_seller_delete.yml")
def product_delete(product_id):
    role = get_jwt_identity().get("role")
    role_id = get_jwt_identity().get("id")
    return service.delete_product(product_id, role, role_id)


@products_blueprint.route("/seller/deleteimage/<int:image_id>", methods=["DELETE"])
@jwt_required()
@swag_from("./products_seller_delete_image.yml")
def product_delete_image(image_id):
    identity = get_jwt_identity()
    data = request.get_json()
    return service.delete_image(identity=identity, image_id=image_id, data=data)
