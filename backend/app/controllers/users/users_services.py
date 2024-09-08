from flask_jwt_extended import create_access_token

from .users_repository import UserRepository
from app.db import db
from ..common import is_filled, get_data_and_validate
from ..cloudinary.cloudinary_service import CloudinaryService


class UserServices:
    def __init__(self, db=db, repository=None, cloudinary_service=None):
        self.cloudinary_service = cloudinary_service or CloudinaryService()
        self.repository = repository or UserRepository()
        self.db = db

    def user_login(self, data):
        try:
            user_data = get_data_and_validate(data, **{"email": str, "password": str})

            if not is_filled(**user_data):
                raise ValueError("Please fill all required fields")

            user = self.repository.get_user_by_email(user_data["email"])

            if not user or not user.check_password(user_data["password"]):
                raise ValueError("Invalid Email / Password")

            if user.is_active == 0:
                raise ValueError("Account is Inactive. Please contact customer service")

            access_token = create_access_token(identity={"id": user.id, "role": "user"})

            return {"access_token": access_token}

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def user_register(self, data):
        try:
            user_data = get_data_and_validate(
                data,
                **{
                    "username": str,
                    "fullname": str,
                    "email": str,
                    "phone_number": str,
                    "password": str,
                },
            )

            if not is_filled(**user_data):
                raise ValueError("Please fill all required fields")

            is_email = self.repository.get_user_by_email(user_data["email"])
            is_username = self.repository.get_user_by_username(user_data["username"])
            is_phone_number = self.repository.get_user_by_phone_number(
                user_data["phone_number"]
            )

            if is_email and is_email.is_active == 0:
                raise ValueError("Please contact customer service")
            if is_email:
                raise ValueError("Email already exists")
            if is_username:
                raise ValueError("Username already exists")
            if is_phone_number:
                raise ValueError("Phone number already exists")

            user = self.repository.user_register(user_data)

            self.db.session.add(user)
            self.db.session.commit()

            return {"message": "User created successfully"}, 201
        except ValueError as e:
            self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            self.db.session.rollback()
            return {"error": str(e)}, 500

    def user_info(self, user_id):
        try:
            user = self.repository.get_user_by_id(user_id)

            return {"user": user.to_dict()}, 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def user_edit(self, user_id, data):
        request_type = data.get("request_type")

        if request_type == "change_email":
            return self.change_email(user_id, data)

        if request_type == "change_password":
            return self.change_password(user_id, data)

        if request_type == "change_phone_number":
            return self.change_phone_number(user_id, data)

    def user_delete(self, user_id, data):
        try:
            password = get_data_and_validate(data, password=str)

            if not is_filled(**password):
                raise ValueError("Please fill all required fields")

            user = self.repository.get_user_by_id(user_id)

            if not user.check_password(password["password"]):
                raise ValueError("Incorrect password")

            user.delete_user()
            self.db.session.commit()

            return {"message": "User deleted successfully"}, 200

        except ValueError as e:
            self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            self.db.session.rollback()
            return {"error": str(e)}, 500

    def change_email(self, user_id, data):
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

            user = self.repository.get_user_by_id(user_id)

            if self.repository.get_user_by_email(edit_data["new_email"]):
                raise ValueError("Email already exists")

            if not user.check_password(edit_data["password"]):
                raise ValueError("Incorrect password")

            user.email = edit_data["new_email"]
            self.db.session.commit()

            return {"message": "Email changed successfully"}, 200

        except ValueError as e:
            self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            self.db.session.rollback()
            return {"error": str(e)}, 500

    def change_password(self, user_id, data):
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

            user = self.repository.get_user_by_id(user_id)

            if not user.check_password(edit_data["password"]):
                raise ValueError("Incorrect password")

            user.password = user.set_password(edit_data["new_password"])
            self.db.session.commit()

            return {"message": "Password changed successfully"}, 200

        except ValueError as e:
            self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            self.db.session.rollback()
            return {"error": str(e)}, 500

    def change_phone_number(self, user_id, data):
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

            if self.repository.get_user_by_phone_number(edit_data["new_phone_number"]):
                raise ValueError("Phone number already use")

            user = self.repository.get_user_by_id(user_id)

            if not user.check_password(edit_data["password"]):
                raise ValueError("Incorrect password")

            user.phone_number = edit_data["new_phone_number"]
            self.db.session.commit()

            return {"message": "Phone number changed successfully"}, 200

        except ValueError as e:
            self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            self.db.session.rollback()
            return {"error": str(e)}, 500

    def refund(self, user_id, amount, commit=True):
        try:
            user = self.repository.get_user_by_id(id=user_id)

            user.refund(amount)

            if commit:
                self.db.session.commit()

            return {"message": "Refund success"}, 200

        except ValueError as e:
            if commit:
                self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            if commit:
                self.db.session.rollback()
            return {"error": str(e)}, 500

    def user_delete_image(self, identity):
        try:
            role_id = identity.get("id")
            role = identity.get("role")

            if role != "user":
                raise ValueError("Unauthorized")

            user = self.repository.get_user_by_id(role_id)

            if not user:
                raise ValueError("User not found")

            public_id = user.image_public_id

            if not public_id:
                raise ValueError("User does not have image")

            self.cloudinary_service.delete_image(public_id)
            user.image_public_id = None
            user.image_url = None

            self.db.session.commit()

            return {"message": "Image deleted successfully"}, 200

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def user_change_image(self, identity, data):
        try:
            role_id = identity.get("id")
            role = identity.get("role")
            image = data.get("image_base64")

            if len(image) != 1:
                raise ValueError("Only one image is allowed")

            if role != "user":
                raise ValueError("Unauthorized")

            user = self.repository.get_user_by_id(role_id)

            if not user:
                raise ValueError("User not found")

            public_id = user.image_public_id
            if public_id:
                self.cloudinary_service.delete_image(public_id)

            image_url = self.cloudinary_service.upload_multiple_images(image)

            user.image_url = image_url[0]["secure_url"]
            user.image_public_id = image_url[0]["public_id"]

            self.db.session.commit()

            return {"message": "Image changed successfully"}, 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500
