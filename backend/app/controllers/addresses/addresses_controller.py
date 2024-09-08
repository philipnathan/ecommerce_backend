from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from

from .addresses_service import AddressesService
from . import addresses_blueprint

service = AddressesService()


@addresses_blueprint.route("/create", methods=["POST"])
@jwt_required()
@swag_from("./address_register.yml")
def user_address_create():
    data = request.get_json()
    identity = get_jwt_identity()
    return service.create_address(data, identity)


@addresses_blueprint.route("/update/<int:address_id>", methods=["PUT"])
@jwt_required()
@swag_from("./address_update.yml")
def address_update(address_id):
    data = request.get_json()
    identity = get_jwt_identity()
    return service.edit_adress(data, identity, address_id)


@addresses_blueprint.route("/delete/<int:address_id>", methods=["DELETE"])
@jwt_required()
@swag_from("./address_delete.yml")
def address_delete(address_id):
    identity = get_jwt_identity()
    return service.delete_address(identity, address_id)


@addresses_blueprint.route("/list", methods=["GET"])
@jwt_required()
@swag_from("./address_get_all.yml")
def address_list():
    identity = get_jwt_identity()
    return service.list_address(identity)


@addresses_blueprint.route("/list/<int:address_id>", methods=["GET"])
@jwt_required()
@swag_from("./address_get_by_id.yml")
def address_by_id(address_id):
    identity = get_jwt_identity()
    return service.get_address_by_id(identity, address_id)
