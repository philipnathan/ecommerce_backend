from app.db import db
from app.models import ProductImages


class ProductImagesRepository:

    def __init__(self, db=db, product_image=ProductImages):
        self.db = db
        self.product_image = product_image

    def get_product_images(self, product_id):
        return self.product_image.query.filter_by(product_id=product_id).all()

    def save_product_image(self, product_id, image_public_id, image_secure_url):
        image = self.product_image(
            product_id=product_id,
            image_public_id=image_public_id,
            image_secure_url=image_secure_url,
        )

        return image

    def get_product_image_by_id(self, image_id):
        return self.product_image.query.filter_by(id=image_id).first()

    def delete_product_image(self, image_id):
        return self.product_image.query.filter_by(id=image_id).delete()
