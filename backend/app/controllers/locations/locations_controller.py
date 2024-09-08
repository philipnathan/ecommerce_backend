from flask import request
from flasgger import swag_from

from . import locations_blueprint
from .locations_services import LocationServices


service = LocationServices()


@locations_blueprint.route("/provinces", methods=["GET"])
@swag_from("./location_all_provinces.yml")
def get_provinces():
    return service.get_provinces()


@locations_blueprint.route("/districts", methods=["GET"])
@swag_from("./location_all_districts.yml")
def get_districts():
    req = request
    return service.get_districts(req)


@locations_blueprint.route("/search", methods=["GET"])
@swag_from("./location_by_id.yml")
def get_location():
    prov_id = request.args.get("prov_id", type=int)
    dist_id = request.args.get("dist_id", type=int)
    return service.get_location_by_id(prov_id, dist_id)
