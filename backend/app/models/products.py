from enum import Enum
from sqlalchemy import (
    Integer,
    VARCHAR,
    Text,
    Column,
    SmallInteger,
    ForeignKey,
    DateTime,
    Float,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import pytz

from app.db import db
from .reviews import Reviews


class Product_Type(Enum):
    STANDARD = 1
    PREMIUM = 2


class Products(db.Model):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)
    weight_kg = Column(Float(5, 2), nullable=False)
    volume_m3 = Column(Float(10, 5), nullable=False)
    length_cm = Column(Integer, nullable=False)
    width_cm = Column(Integer, nullable=False)
    height_cm = Column(Integer, nullable=False)
    stock = Column(SmallInteger, nullable=False)
    product_type = Column(Integer, nullable=False)
    category_id = Column(SmallInteger, ForeignKey("categories.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    is_active = Column(SmallInteger, default=1, nullable=False)
    sold_qty = Column(Integer, default=0, nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(pytz.utc)
    )
    updated_at = Column(
        DateTime, nullable=True, onupdate=lambda: datetime.now(pytz.utc)
    )

    reviews = relationship("Reviews", backref="product_reviews")
    product_orders = relationship("ProductOrders", backref="product_orders")
    product_images = relationship("ProductImages", backref="product_images")

    def __init__(
        self,
        name,
        description,
        price,
        weight_kg,
        stock,
        product_type,
        category_id,
        seller_id,
        length_cm,
        width_cm,
        height_cm,
    ):
        self.name = name
        self.description = description
        self.price = price
        self.weight_kg = weight_kg
        self.stock = stock
        self.product_type = product_type
        self.category_id = category_id
        self.seller_id = seller_id
        self.length_cm = length_cm
        self.width_cm = width_cm
        self.height_cm = height_cm
        self.volume_m3 = self.length_cm * self.width_cm * self.height_cm / 1_000_000

    def to_dict(self):
        all_reviews = self.reviews
        reviews = [review.to_dict() for review in all_reviews]

        avg_rating = (
            db.session.query(func.avg(Reviews.rating))
            .filter(Reviews.product_id == self.id)
            .scalar()
        )

        seller = self.seller_products.to_dict()
        seller_info = {
            "store_name": seller["store_name"],
            "store_image_url": seller["store_image_url"],
            "store_district": seller["addresses"][0]["district_name"],
        }

        product_images = self.product_images
        if len(product_images) > 0:
            images = [image.to_dict() for image in product_images]
        else:
            images = None

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "weight_kg": round(self.weight_kg, 2),
            "volume_m3": round(self.volume_m3, 2),
            "stock": self.stock,
            "image_url": images,
            "product_type": self.product_type,
            "category_id": self.category_id,
            "is_active": self.is_active,
            "sold_qty": self.sold_qty,
            "reviews": reviews,
            "avg_rating": round(avg_rating, 2) if avg_rating else None,
            "seller_id": self.seller_id,
            "seller_info": seller_info,
            "created_at": self.created_at,
        }

    def to_cart(self):
        seller = self.seller_products.to_dict()
        seller_info = {
            "store_name": seller["store_name"],
            "store_immage_url": seller["store_image_url"],
        }

        product_images = self.product_images
        if len(product_images) > 0:
            images = [image.to_dict() for image in product_images]
        else:
            images = None

        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "stock": self.stock,
            "image_url": images,
            "category_id": self.category_id,
            "category_name": self.category_products.category_name,
            "is_active": self.is_active,
            "seller_id": self.seller_products.id,
            "seller_info": seller_info,
            "store_name": self.seller_products.store_name,
        }

    def upload_image(self):
        pass

    def item_sold(self, qty):
        self.sold_qty += qty

    def reduce_item_qty(self, qty):
        self.stock -= qty

    def increase_item_qty(self, qty):
        self.stock += qty
