from app.db import db
from .product_images_repository import ProductImagesRepository
from ..cloudinary.cloudinary_service import CloudinaryService


class ProductImagesService:

    def __init__(self, db=db, repository=None, cloudinary_service=None):
        self.db = db
        self.repository = repository or ProductImagesRepository()
        self.cloudinary_service = cloudinary_service or CloudinaryService()

    def save_image(self, product_id, new_images_base64):
        """
        {
            "product_id": 1,
            images_data: [
                "base_64_image_1",
                "base_64_image_2"
            ]
        }
        """
        try:
            product_images = self.repository.get_product_images(product_id)
            number_of_image = len(product_images)

            if number_of_image > 5 or number_of_image + len(new_images_base64) > 5:
                raise ValueError(
                    "Cannot upload more than 5 images. Please delete some images first."
                )

            images_details = self.cloudinary_service.upload_multiple_images(
                new_images_base64
            )

            if len(images_details) <= 0:
                raise ValueError("Failed to upload images")

            result = []
            for image in images_details:
                new_image = self.repository.save_product_image(
                    product_id=product_id,
                    image_public_id=image["public_id"],
                    image_secure_url=image["secure_url"],
                )
                result.append(new_image)
                number_of_image += 1

            self.db.session.add_all(result)
            self.db.session.commit()

            return {"message": "Product images created successfully"}, 201

        except ValueError as e:
            self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            self.db.session.rollback()
            return {"error": str(e)}, 500

    def delete_image(self, image_id, image_public_id, product_id):
        try:
            product_image = self.repository.get_product_image_by_id(image_id)

            if (
                not product_image
                or product_image.product_id != product_id
                or product_image.image_public_id != image_public_id
            ):
                raise ValueError("Product image not found")

            self.repository.delete_product_image(image_id=image_id)
            self.db.session.commit()

            self.cloudinary_service.delete_image(image_public_id)

            return {"message": "Product image deleted successfully"}, 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500
