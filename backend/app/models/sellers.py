from sqlalchemy import Column, Integer, VARCHAR, TEXT, SmallInteger, DateTime
from sqlalchemy.orm import relationship
import bcrypt
from enum import Enum
from datetime import datetime
import pytz

from ..db import db


class Is_Active_Status(Enum):
    INACTIVE = 0
    ACTIVE = 1


class Sellers(db.Model):
    __tablename__ = "sellers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(VARCHAR(50), unique=True, nullable=False)
    password = Column(VARCHAR(255), nullable=False)
    phone_number = Column(VARCHAR(14), unique=True, nullable=False)
    store_name = Column(VARCHAR(30), unique=True, nullable=False)
    store_description = Column(TEXT, nullable=True)
    store_image_url = Column(VARCHAR(255), nullable=True)
    store_image_public_id = Column(VARCHAR(255), nullable=True)
    is_active = Column(
        SmallInteger, default=Is_Active_Status.ACTIVE.value, nullable=False
    )
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(pytz.UTC)
    )
    updated_at = Column(
        DateTime, nullable=True, onupdate=lambda: datetime.now(pytz.UTC)
    )
    balance = Column(Integer, default=0, nullable=False)

    shipping_options = relationship("ShippingOptions", backref="seller_shippingoptions")
    seller_vouchers = relationship("SellerVouchers", backref="seller_selllervouchers")
    transactions = relationship("Transactions", backref="seller_transactions")
    products = relationship("Products", backref="seller_products")
    reviews = relationship("Reviews", backref="seller_reviews")
    addresses = relationship("Addresses", backref="seller_addresses")

    def __init__(
        self,
        email,
        password,
        phone_number,
        store_name,
    ):
        self.email = email
        self.password = self.set_password(password)
        self.phone_number = phone_number
        self.store_name = store_name

    def set_password(self, password):
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))

    def to_dict(self):
        all_addresses = self.addresses
        addresses = [address.to_dict() for address in all_addresses]

        return {
            "id": self.id,
            "email": self.email,
            "phone_number": self.phone_number,
            "store_name": self.store_name,
            "store_description": self.store_description,
            "addresses": addresses if addresses else [],
            "store_image_url": self.store_image_url,
        }

    def delete_seller(self):
        self.is_active = Is_Active_Status.INACTIVE.value

    def add_balance(self, amount):
        self.balance += amount
