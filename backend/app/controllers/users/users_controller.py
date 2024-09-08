from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from

from . import users_blueprint
from .users_services import UserServices

service = UserServices()


@users_blueprint.route("/login", methods=["POST"])
@swag_from("./user_login.yml")
def user_login():
    data = request.get_json()
    return service.user_login(data)


@users_blueprint.route("register", methods=["POST"])
@swag_from("./user_register.yml")
def user_register():
    data = request.get_json()
    return service.user_register(data)


@users_blueprint.route("/me", methods=["GET"])
@jwt_required()
@swag_from("./user_info.yml")
def user_info():
    identity = get_jwt_identity()
    user_id = identity.get("id")
    return service.user_info(user_id)


@users_blueprint.route("/update", methods=["PUT"])
@jwt_required()
@swag_from("./user_edit.yml")
def user_edit():
    identity = get_jwt_identity()
    user_id = identity.get("id")
    data = request.get_json()
    return service.user_edit(user_id, data)


@users_blueprint.route("/delete", methods=["DELETE"])
@jwt_required()
@swag_from("./user_delete.yml")
def user_delete():
    identity = get_jwt_identity()
    user_id = identity.get("id")
    data = request.get_json()
    return service.user_delete(user_id, data)


@users_blueprint.route("/update/image", methods=["PUT"])
@jwt_required()
@swag_from("./user_update_image.yml")
def user_update_image():
    identity = get_jwt_identity()
    data = request.get_json()
    return service.user_change_image(identity=identity, data=data)


@users_blueprint.route("/delete/image", methods=["DELETE"])
@jwt_required()
@swag_from("./user_delete_image.yml")
def user_delete_image():
    identity = get_jwt_identity()
    return service.user_delete_image(identity=identity)
