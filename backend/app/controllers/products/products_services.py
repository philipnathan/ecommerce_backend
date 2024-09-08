from .products_repository import ProductsRepository
from ..sellers.sellers_service import SellersServices
from ..cloudinary.cloudinary_service import CloudinaryService
from ..product_images.product_images_service import ProductImagesService

from app.db import db
from ..common import is_filled, get_data_and_validate


class ProductsServices:
    def __init__(
        self,
        db=db,
        repository=None,
        seller_service=None,
        cloudinary_service=None,
        product_images_service=None,
    ):
        self.db = db
        self.repository = repository or ProductsRepository()
        self.seller_service = seller_service or SellersServices()
        self.cloudinary_service = cloudinary_service or CloudinaryService()
        self.product_images_service = product_images_service or ProductImagesService()

    def create_product(self, data, role, role_id):
        try:
            keys = [
                "name",
                "description",
                "price",
                "weight_kg",
                "stock",
                "product_type",
                "category_id",
                "length_cm",
                "width_cm",
                "height_cm",
            ]

            seller_info_address = self.check_role_and_id(role, role_id)["seller"][
                "addresses"
            ]

            if not seller_info_address or len(seller_info_address) <= 0:
                raise ValueError("Must input an address before creating a product")

            all_data = self.all_data(data)
            images_base64 = data.get("image_base64", None)

            if not is_filled(**all_data):
                raise ValueError("Please fill all required fields")
            for key in keys:
                if key not in all_data:
                    raise ValueError(f"Please fill {key} field")
            if not images_base64:
                raise ValueError("Please upload at least one image")

            new_product = self.repository.create_product(seller_id=role_id, **all_data)

            self.db.session.add(new_product)
            self.db.session.commit()

            # save to db and upload to cloudinary
            product_id = new_product.id
            message, status_code = self.product_images_service.save_image(
                product_id=product_id, new_images_base64=images_base64
            )

            if status_code not in [200, 201]:
                raise ValueError(message["error"])

            return {"message": "Product created successfully"}, 201

        except (TypeError, ValueError) as e:
            self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            self.db.session.rollback
            return {"error": str(e)}, 500

    def get_list_products(self, request, role, role_id=None):
        self.check_role_and_id(role, role_id)

        try:
            per_page = request.args.get("per_page", 10, int)
            page = request.args.get("page", 1, int)

            products = self.repository.get_list_products(
                role=role, page=page, per_page=per_page, role_id=role_id
            )
            return self.response(products=products), 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def get_product_by_id(self, product_id, role, role_id=None):
        self.check_role_and_id(role, role_id)

        try:
            product = self.repository.get_product_by_id(
                role=role, product_id=product_id, role_id=role_id
            )

            if product is None:
                raise ValueError("Product not found")

            return product.to_dict(), 200

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def update_product(self, product_id, role, role_id, data):
        self.check_role_and_id(role, role_id)

        try:
            all_data = self.all_data(data)
            image_base64 = data.get("image_base64")

            product = self.repository.get_product_by_id(
                product_id=product_id, role=role, role_id=role_id
            )
            count_updated_key = 0
            key_updated = []

            if product is None:
                raise ValueError("Product not found")

            for key, data in all_data.items():
                if data is None:
                    continue
                if data and hasattr(product, key):
                    setattr(product, key, data)
                    count_updated_key += 1
                    key_updated.append(key)

            if image_base64:
                message, status_code = self.product_images_service.save_image(
                    product_id=product_id, new_images_base64=image_base64
                )

                if status_code not in [200, 201]:
                    raise ValueError(message["error"])

                count_updated_key += 1
                key_updated.append("images")

            if count_updated_key == 0:
                raise ValueError("No data to update")

            self.db.session.commit()

            return {
                "message": "Product updated successfully",
                "key_updated": key_updated,
            }, 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def delete_product(self, product_id, role, role_id):
        self.check_role_and_id(role, role_id)

        try:
            product = self.repository.get_product_by_id(
                role=role, product_id=product_id, role_id=role_id
            )

            if product is None:
                raise ValueError("Product not found")

            product.is_active = 0

            self.db.session.commit()
            return {"message": "Product deleted successfully"}, 200

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def delete_image(self, identity, image_id, data):
        try:
            product_id = data.get("product_id")
            image_public_id = data.get("image_public_id")

            if not product_id or not image_public_id:
                raise ValueError("Please provide product_id and image_public_id")

            self.check_role_and_id(role=identity["role"], role_id=identity["id"])

            product = self.get_product_by_id(
                role=identity["role"],
                product_id=product_id,
                role_id=identity["id"],
            )

            if product is None:
                raise ValueError("Product not found")

            message, result = self.product_images_service.delete_image(
                image_id=image_id,
                image_public_id=image_public_id,
                product_id=product_id,
            )

            if result != 200:
                raise ValueError(message["error"])

            return {"message": "Image deleted successfully"}, 200

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def check_role_and_id(self, role, role_id):
        if role != "seller":
            return {"error": "Unauthorized"}, 401
        if role_id is None:
            return {"error": "Invalid seller"}, 400

        seller_info = self.seller_service.seller_info(role_id)

        if seller_info[1] != 200:
            raise ValueError("Seller not found")

        return seller_info[0]

    def all_data(self, data):
        return get_data_and_validate(
            data,
            name=str,
            description=str,
            price=int,
            weight_kg=float,
            stock=int,
            product_type=int,
            category_id=int,
            length_cm=int,
            width_cm=int,
            height_cm=int,
        )

    def response(self, products):
        return {
            "products": [product.to_dict() for product in products],
            "total_page": products.pages,
            "current_page": products.page,
            "total_items": products.total,
        }

    def transaction_success_modification(self, product_id, quantity, commit=True):
        try:
            product = self.repository.get_product_by_id(
                product_id=product_id, role="user"
            )

            product.item_sold(quantity)
            product.reduce_item_qty(quantity)

            if commit:
                self.db.session.commit()

            return {
                "message": "Product stock and sold quantity updated successfully"
            }, 200

        except ValueError as e:
            if commit:
                self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            if commit:
                self.db.session.rollback()
            return {"error": str(e)}, 500

    def transaction_canceled_modification(self, product_id, quantity, commit=True):
        try:
            product = self.repository.get_product_by_id(
                product_id=product_id, role="user"
            )

            product.item_sold(-quantity)
            product.increase_item_qty(quantity)

            if commit:
                self.db.session.commit()

            return {
                "message": "Product stock and sold quantity updated successfully"
            }, 200
        except ValueError as e:
            if commit:
                self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            if commit:
                self.db.session.rollback()
            return {"error": str(e)}, 500
