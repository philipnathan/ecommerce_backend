from flask_jwt_extended import jwt_required
from flasgger import swag_from

from . import shipments_blueprint
from .shipments_service import ShipmentsService

service = ShipmentsService()


@shipments_blueprint.route("/list", methods=["GET"])
@jwt_required()
@swag_from("./shipment_get_list.yml")
def shipment_list():
    return service.list_shipments()
