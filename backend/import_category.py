import json
from app import create_app

from app.db import db
from app.models import Categories


def read_json(filename):
    with open(filename, "r") as f:
        return json.load(f)


def import_categories(data, model):
    app = create_app()

    with app.app_context():
        try:
            new_records = []
            for category in data:
                new_category = model(**category)
                new_records.append(new_category)

            db.session.bulk_save_objects(new_records)
            db.session.commit()
            print("Categories imported successfully")
        except Exception as e:
            print(e)


import_categories(read_json("category.json"), Categories)
