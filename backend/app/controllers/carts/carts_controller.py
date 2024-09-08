from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from

from . import carts_blueprint
from .carts_service import CartsService


service = CartsService()


@carts_blueprint.route("/list", methods=["GET"])
@jwt_required()
@swag_from("./carts_get_list.yml")
def cart_list():
    identity = get_jwt_identity()
    user_id = identity.get("id")
    return service.list_cart(user_id)


@carts_blueprint.route("/createupdate", methods=["POST"])
@jwt_required()
@swag_from("./carts_create_list.yml")
def cart_create():
    data = request.get_json()
    identity = get_jwt_identity()
    return service.create_update_cart(data, identity)


@carts_blueprint.route("/delete/<int:product_id>", methods=["DELETE"])
@jwt_required()
@swag_from("./carts_delete_item.yml")
def cart_delete(product_id):
    identity = get_jwt_identity()
    return service.delete_cart(product_id=product_id, identity=identity)
