from app.db import db
from app.models import Addresses


class AddressesRepository:
    def __init__(self, db=db, address=Addresses):
        self.db = db
        self.address = address

    def create_address(self, data):
        return self.address(**data)

    def get_list_address(self, role_id, role):
        query = self.address.query.filter(self.address.is_active == 1)

        if role == "user":
            query = query.filter_by(user_id=role_id)

        if role == "seller":
            query = query.filter_by(seller_id=role_id)

        return query.all()

    def get_address_by_filter(self, address_id, role_id, role):
        query = self.address.query.filter(self.address.is_active == 1)

        if role == "user":
            query = query.filter_by(user_id=role_id, id=address_id)

        if role == "seller":
            query = query.filter_by(seller_id=role_id, id=address_id)

        return query.first()
