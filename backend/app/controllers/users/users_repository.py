from app.db import db
from app.models import Users


class UserRepository:
    def __init__(self, db=db, user=Users):
        self.db = db
        self.user = user

    def get_user_by_email(self, email):
        return self.user.query.filter_by(email=email).first()

    def get_user_by_username(self, username):
        return self.user.query.filter_by(username=username).first()

    def get_user_by_phone_number(self, phone_number):
        return self.user.query.filter_by(phone_number=phone_number).first()

    def get_user_by_id(self, id):
        return self.user.query.filter_by(id=id).first()

    def user_register(self, data):
        new_user = self.user(**data)

        return new_user
