from flask import request
from flasgger import swag_from
from flask_jwt_extended import jwt_required, get_jwt_identity


from . import shipping_options_blueprint
from .shipping_options_service import ShippingOptionsService

service = ShippingOptionsService()


@shipping_options_blueprint.route("/update", methods=["PUT"])
@jwt_required()
@swag_from("./shipping_options_update.yml")
def option_update():
    data = request.get_json()
    identity = get_jwt_identity()
    return service.update_option(data=data, identity=identity)


@shipping_options_blueprint.route("/list", methods=["GET"])
@jwt_required()
@swag_from("./shipping_options_get_list.yml")
def option_list():
    identity = get_jwt_identity()
    return service.get_option_list(identity=identity)
