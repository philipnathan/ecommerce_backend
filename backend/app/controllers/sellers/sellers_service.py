from flask_jwt_extended import create_access_token

from .sellers_repository import SellersRepository
from ..locations.locations_repository import LocationRepository
from app.db import db
from ..common import is_filled, get_data_and_validate
from ..cloudinary.cloudinary_service import CloudinaryService


class SellersServices:
    def __init__(self, db=db, repository=None, location=None, cloudinary_service=None):
        self.repository = repository or SellersRepository()
        self.location = location or LocationRepository()
        self.db = db
        self.cloudinary_service = cloudinary_service or CloudinaryService()

    def seller_login(self, data):
        try:
            seller_data = get_data_and_validate(data, email=str, password=str)

            if not is_filled(**seller_data):
                raise ValueError("Please fill all required fields")

            seller = self.repository.get_seller_by_email(seller_data["email"])

            if not seller:
                raise ValueError("Invalid email / password")

            if seller.is_active == 0:
                raise ValueError("Account is Inactive. Please contact customer service")

            if not seller.check_password(seller_data["password"]):
                raise ValueError("Invalid email / password")

            access_token = create_access_token(
                identity={"id": seller.id, "role": "seller"}
            )

            return {"access_token": access_token}, 200

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def seller_register(self, data):
        try:
            new_seller_data = get_data_and_validate(
                data,
                **{
                    "email": str,
                    "phone_number": str,
                    "store_name": str,
                    "password": str,
                },
            )

            if not is_filled(**new_seller_data):
                raise ValueError("Please fill all required fields")

            self.if_exist_raise_error(
                email=new_seller_data["email"],
                phone_number=new_seller_data["phone_number"],
                store_name=new_seller_data["store_name"],
            )

            new_seller = self.repository.seller_register(new_seller_data)

            self.db.session.add(new_seller)
            self.db.session.commit()

            return {"message": "Seller registered successfully"}, 200

        except ValueError as e:
            self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            self.db.session.rollback()
            return {"error": str(e)}, 500

    def seller_info(self, seller_id):
        try:
            seller = self.repository.get_seller_by_id(seller_id)

            if not seller:
                raise ValueError("Seller not found")

            return {"seller": seller.to_dict()}, 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def seller_edit_personal(self, seller_id, data):
        request_type = data.get("request_type")

        if request_type == "change_email":
            return self.change_email(seller_id, data)

        if request_type == "change_password":
            return self.change_password(seller_id, data)

        if request_type == "change_phone_number":
            return self.change_phone_number(seller_id, data)

    def seller_edit_business(self, seller_id, data):
        all_data = get_data_and_validate(
            data,
            **{
                "store_name": str,
                "store_description": str,
            },
        )

        try:
            seller = self.repository.get_seller_by_id(seller_id)
            count_updated_key = 0
            key_updated = []

            for key, data in all_data.items():
                # check if store_name is already used
                if key == "store_name" and data is not None:
                    self.if_exist_raise_error(store_name=data)

                # update if data is not None and seller has that key
                if data is not None and hasattr(seller, key):
                    setattr(seller, key, data)
                    count_updated_key += 1
                    key_updated.append(key)

            if key == "store_image_url" and data.get("store_image_url"):
                if seller.store_image_url:
                    identity = {"id": seller_id, "role": "seller"}
                    delete, status_code = self.seller_delete_image(identity=identity)

                    if status_code not in [200, 201]:
                        raise ValueError("Failed to delete previous image")
                    if len(data.get("store_image_url")) != 1:
                        raise ValueError("Please upload only one image")

                result = self.cloudinary_service.upload_multiple_images(
                    data["store_image_url"]
                )

                seller.store_image_url = result[0]["secure_url"]
                seller.store_image_public_id = result[0]["public_id"]
                count_updated_key += 1
                key_updated.append("store_image_url")

            if count_updated_key == 0:
                raise ValueError("No data is updated")

            self.db.session.commit()

            return {
                "message": "Seller business information updated successfully",
                "key_updated": key_updated,
            }, 200

        except ValueError as e:
            self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            self.db.session.rollback()
            return {"error": str(e)}, 500

    def seller_delete(self, seller_id, data):
        password = data.get("password")

        try:
            if not is_filled(password=password):
                raise ValueError("Please input your password")

            seller = self.repository.get_seller_by_id(seller_id)

            if not seller:
                raise ValueError("Seller not found")

            if seller.is_active == 0:
                raise ValueError("Seller already deleted")

            if not seller.check_password(password):
                raise ValueError("Incorrect password")

            seller.delete_seller()
            self.db.session.commit()

            return {"message": "Seller deleted successfully"}, 200

        except ValueError as e:
            self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            self.db.session.rollback()
            return {"error": str(e)}, 500

    def seller_public_info(self, seller_id):
        try:
            seller_info = self.repository.get_seller_by_id(seller_id)

            if not seller_info:
                raise ValueError("Seller not found")

            seller_info = seller_info.to_dict()

            pop_keys = ["email", "phone_number"]
            for key in pop_keys:
                seller_info.pop(key, None)

            pop_address_key = [
                "address_line",
                "address_type",
                "phone_number",
                "receiver_name",
                "rt_rw",
            ]

            if seller_info["addresses"]:
                for key in pop_address_key:
                    seller_info["addresses"][0].pop(key, None)

            return {"seller": seller_info}, 200

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def change_email(self, seller_id, data):
        try:
            edit_data = get_data_and_validate(
                data,
                **{
                    "new_email": str,
                    "password": str,
                },
            )

            if not is_filled(**edit_data):
                raise ValueError("Please fill all required fields")

            seller = self.change_personal_checker(
                seller_id=seller_id,
                key="email",
                password=edit_data["password"],
                new_data=edit_data["new_email"],
            )

            seller.email = edit_data["new_email"]
            self.db.session.commit()

            return {"message": "Email changed successfully"}, 200

        except ValueError as e:
            self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            self.db.session.rollback()
            return {"error": str(e)}, 500

    def change_password(self, seller_id, data):

        try:
            edit_data = get_data_and_validate(
                data,
                **{
                    "password": str,
                    "new_password": str,
                },
            )

            if not is_filled(**edit_data):
                raise ValueError("Please fill all required fields")

            seller = self.change_personal_checker(
                seller_id=seller_id,
                key="password",
                password=edit_data["password"],
                new_data=edit_data["new_password"],
            )

            seller.password = seller.set_password(edit_data["new_password"])
            self.db.session.commit()

            return {"message": "Password changed successfully"}, 200

        except ValueError as e:
            self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            self.db.session.rollback()
            return {"error": str(e)}, 500

    def change_phone_number(self, seller_id, data):
        try:
            edit_data = get_data_and_validate(
                data,
                **{
                    "password": str,
                    "new_phone_number": str,
                },
            )

            if not is_filled(**edit_data):
                raise ValueError("Please fill all required fields")

            seller = self.change_personal_checker(
                seller_id=seller_id,
                key="phone_number",
                password=edit_data["password"],
                new_data=edit_data["new_phone_number"],
            )

            seller.phone_number = edit_data["new_phone_number"]
            self.db.session.commit()

            return {"message": "Phone number changed successfully"}, 200

        except ValueError as e:
            self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            self.db.session.rollback()
            return {"error": str(e)}, 500

    def change_personal_checker(self, seller_id, password, key, new_data):
        try:
            seller = self.repository.get_seller_by_id(seller_id)

            if not seller:
                raise ValueError("Seller not found")
            if not seller.check_password(password):
                raise ValueError("Incorrect password")

            data = {key: new_data}
            if key != "password" and self.if_exist_raise_error(**data):
                raise ValueError(f"{key} already used")

            return seller
        except ValueError as e:
            raise e
        except Exception as e:
            raise e

    def if_exist_raise_error(self, **kwargs):
        for key, value in kwargs.items():
            try:
                if key == "email" and self.repository.get_seller_by_email(value):
                    raise ValueError("Email already exists")
                if (
                    key == "phone_number"
                    and self.repository.get_seller_by_phone_number(value)
                ):
                    raise ValueError("Phone number already used")
                if key == "store_name" and self.repository.get_seller_by_store_name(
                    value
                ):
                    raise ValueError("Store name already used")
            except ValueError as e:
                raise e
            except Exception as e:
                raise e

    def add_balanced_transaction_delivered(self, seller_id, amount):
        try:
            seller = self.repository.get_seller_by_id(seller_id)

            if not seller:
                raise ValueError("Seller not found")

            seller.add_balance(amount)

        except ValueError as e:
            raise e
        except Exception as e:
            raise e

    def seller_delete_image(self, identity):
        try:
            role_id = identity.get("id")
            role = identity.get("role")

            if role != "seller":
                raise ValueError("Unauthorized access")

            seller = self.repository.get_seller_by_id(role_id)

            if not seller:
                raise ValueError("Seller not found")

            public_id = seller.store_image_public_id

            if not public_id:
                raise ValueError("Seller does not have image")

            self.cloudinary_service.delete_image(public_id)
            seller.store_image_public_id = None
            seller.store_image_url = None

            self.db.session.commit()

            return {"message": "Image deleted successfully"}, 200

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500
