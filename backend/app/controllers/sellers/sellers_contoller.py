from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from

from .sellers_service import SellersServices
from . import sellers_blueprint

service = SellersServices()


@sellers_blueprint.route("/login", methods=["POST"])
@swag_from("./seller_login.yml")
def seller_login():
    data = request.get_json()
    return service.seller_login(data)


@sellers_blueprint.route("/register", methods=["POST"])
@swag_from("./seller_register.yml")
def seller_register():
    data = request.get_json()
    return service.seller_register(data)


@sellers_blueprint.route("/me", methods=["GET"])
@jwt_required()
@swag_from("./seller_info.yml")
def seller_info():
    identity = get_jwt_identity()
    seller_id = identity.get("id")
    return service.seller_info(seller_id)


@sellers_blueprint.route("/publicinfo/<int:seller_id>", methods=["GET"])
@swag_from("./seller_public_info.yml")
def seller_public_info(seller_id):
    return service.seller_public_info(seller_id)


@sellers_blueprint.route("/update/personal", methods=["PUT"])
@jwt_required()
@swag_from("./seller_update_personal.yml")
def seller_edit_personal():
    identity = get_jwt_identity()
    seller_id = identity.get("id")
    data = request.get_json()
    return service.seller_edit_personal(seller_id, data)


@sellers_blueprint.route("/update/business", methods=["PUT"])
@jwt_required()
@swag_from("./seller_update_business.yml")
def seller_edit_business():
    identity = get_jwt_identity()
    seller_id = identity.get("id")
    data = request.get_json()
    return service.seller_edit_business(seller_id, data)


@sellers_blueprint.route("/delete", methods=["DELETE"])
@jwt_required()
@swag_from("./seller_delete.yml")
def seller_delete():
    identity = get_jwt_identity()
    seller_id = identity.get("id")
    data = request.get_json()
    return service.seller_delete(seller_id, data)


@sellers_blueprint.route("/deleteimage", methods=["DELETE"])
@jwt_required()
@swag_from("./seller_delete_image.yml")
def seller_delete_image():
    identity = get_jwt_identity()
    return service.seller_delete_image(identity=identity)
