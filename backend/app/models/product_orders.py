from app.db import db

from sqlalchemy import VARCHAR
from datetime import datetime
import pytz


class ProductOrders(db.Model):
    __tablename__ = "product_orders"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    transaction_id = db.Column(
        VARCHAR(30), db.ForeignKey("transactions.id"), nullable=False
    )
    quantity = db.Column(db.SmallInteger, nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(pytz.UTC)
    )
    updated_at = db.Column(
        db.DateTime, nullable=True, onupdate=lambda: datetime.now(pytz.UTC)
    )

    def __init__(self, product_id, transaction_id, quantity):
        self.product_id = product_id
        self.transaction_id = transaction_id
        self.quantity = quantity

    def to_dict(self):
        product = self.product_orders.to_cart()

        product_info = {
            "is_active": product["is_active"],
            "image_url": (
                product.get("image_url")[0]["image_secure_url"]
                if product["image_url"]
                else None
            ),
            "name": product["name"],
            "price": product["price"],
        }
        return {
            "product_order_id": self.id,
            "product_id": self.product_id,
            "product_info": product_info,
            "quantity": self.quantity,
        }
