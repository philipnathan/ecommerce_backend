from app.db import db
from app.models import Sellers


class SellersRepository:
    def __init__(self, db=db, seller=Sellers):
        self.db = db
        self.seller = seller

    def get_seller_by_email(self, email):
        return self.seller.query.filter_by(email=email).first()

    def get_seller_by_store_name(self, store_name):
        return self.seller.query.filter_by(store_name=store_name).first()

    def get_seller_by_phone_number(self, phone_number):
        return self.seller.query.filter_by(phone_number=phone_number).first()

    def get_seller_by_id(self, seller_id):
        return self.seller.query.filter_by(id=seller_id).first()

    def seller_register(self, new_seller_data):
        return self.seller(**new_seller_data)
