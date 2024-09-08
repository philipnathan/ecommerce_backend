from app.db import db
from .categories_repository import CategoriesRepository


class CategoriesService:
    def __init__(self, db=db, repository=None):
        self.db = db
        self.repository = repository or CategoriesRepository()

    def get_categories(self):
        try:
            categories = self.repository.get_categories()

            return [category.to_dict() for category in categories]

        except Exception as e:
            return {"error": str(e)}
