from app.db import db
from .locations_repository import LocationRepository


class LocationServices:
    def __init__(self, db=db, repository=None):
        self.db = db
        self.repository = repository or LocationRepository()

    def get_provinces(self):
        try:
            return [data.to_dict() for data in self.repository.get_provinces()]
        except Exception as e:
            return {"error": str(e)}, 500

    def get_districts(self, req):
        try:
            province_id = req.args.get("prov_id")

            districts = self.repository.get_districts(province_id=province_id)

            if not districts:
                raise ValueError("District not found")

            return [district.to_dict() for district in districts]

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def get_location_by_id(self, prov_id, dist_id):
        try:
            if dist_id:
                district = self.repository.get_districts_by_id(dist_id)
                if district is None:
                    raise ValueError("District not found")
                return district.to_dict()

            if prov_id:
                province = self.repository.get_provinces_by_id(prov_id)
                if province is None:
                    raise ValueError("Province not found")
                return province.to_dict()

        except Exception as e:
            return {"error": str(e)}, 500
