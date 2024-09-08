from datetime import datetime
import pytz

from app.db import db


class ProductImages(db.Model):
    __tablename__ = "product_images"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    image_public_id = db.Column(db.String(255), nullable=False)
    image_secure_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(pytz.UTC)
    )

    def __init__(self, product_id, image_public_id, image_secure_url):
        self.product_id = product_id
        self.image_public_id = image_public_id
        self.image_secure_url = image_secure_url

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "image_public_id": self.image_public_id,
            "image_secure_url": self.image_secure_url,
        }
