from app.db import db
from app.models import Provinces, Districts


class LocationRepository:
    def __init__(self, db=db, province=Provinces, district=Districts):

        self.db = db
        self.province = province
        self.district = district

    def get_provinces(self):
        return self.province.query.all()

    def get_districts(self, province_id=None):
        query = self.district.query

        if province_id:
            query = query.filter_by(province_id=province_id)

        return query.all()

    def get_provinces_by_id(self, province_id):
        return self.province.query.filter_by(id=province_id).first()

    def get_districts_by_id(self, district_id):
        return self.district.query.filter_by(id=district_id).first()
