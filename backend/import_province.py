import json
from app import create_app

from app.db import db
from app.models import Provinces, Districts


def read_json(filename):
    with open(filename, "r") as f:
        return json.load(f)


def import_province_district(data, model, keypair_data):
    app = create_app()

    with app.app_context():
        try:
            new_records = []
            new_ids = set()
            existing_ids = {record.id for record in model.query.all()}

            for value in data["rajaongkir"]["results"]:
                new_data = model()
                skip_record = False

                for pairkey, pairvalue in keypair_data.items():
                    incomingkey = list(pairvalue.keys())[0]
                    datatype = list(pairvalue.values())[0]

                    if pairkey == "id" and (
                        value[incomingkey] in existing_ids
                        or value[incomingkey] in new_ids
                    ):
                        skip_record = True
                        break
                    else:
                        new_ids.add(value[incomingkey])

                    converted_value = datatype(value[incomingkey])
                    setattr(new_data, pairkey, converted_value)

                if skip_record:
                    continue

                new_records.append(new_data)

            db.session.bulk_save_objects(new_records)
            db.session.commit()
            print("Successfully import data")
        except Exception as e:
            db.session.rollback()
            print(e)


import_province_district(
    data=read_json("rajaongkir.json"),
    model=Provinces,
    keypair_data={
        "id": {"province_id": int},
        "province": {"province": str},
    },
)


import_province_district(
    data=read_json("rajaongkir.json"),
    model=Districts,
    keypair_data={
        "id": {"city_id": int},
        "district": {"city_name": str},
        "province_id": {"province_id": int},
    },
)
