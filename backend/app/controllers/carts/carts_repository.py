from app.db import mongo


class CartsRepository:
    def __init__(self, db=None):
        self.collection = mongo

    def find_cart_by_user_id(self, user_id):
        return self.collection.db.carts.find_one({"_id": user_id})

    def insert_cart(self, user_id, items):
        return self.collection.db.carts.update_one(
            {"_id": user_id}, {"$set": {"items": [items]}}, upsert=True
        )

    def find_one(self, user_id, product_id):
        return self.collection.db.carts.find_one(
            {"_id": user_id, "items.product_id": product_id}
        )

    def update_existed(self, user_id, product_id, quantity):
        self.collection.db.carts.update_one(
            {"_id": user_id, "items.product_id": product_id},
            {"$set": {"items.$.quantity": quantity}},
        )

    def update_new(self, user_id, items):
        self.collection.db.carts.update_one(
            {"_id": user_id},
            {"$push": {"items": items}},
        )

    def delete_one(self, user_id, product_id):
        self.collection.db.carts.update_one(
            {"_id": user_id}, {"$pull": {"items": {"product_id": product_id}}}
        )
