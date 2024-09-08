from app.db import db
from app.models import Categories


class CategoriesRepository:
    def __init__(self, db=db, category=Categories):
        self.db = db
        self.category = category

    def get_category_by_name(self, category_name):
        return self.category.query.filter_by(category_name=category_name).first()

    def get_categories(self):
        return self.category.query.all()
