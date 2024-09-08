from app.db import db
from app.models import Transactions


class TransactionsRepository:
    def __init__(self, db=db, transaction=Transactions):
        self.db = db
        self.transaction = transaction

    def create_transaction(self, data):
        return self.transaction(**data)

    def get_transaction_by_user_id(
        self, role, role_id, date=None, page=1, per_page=10, tx=None, status=None
    ):
        query = self.transaction.query

        if role == "user":
            query = query.filter_by(user_id=role_id)
        if role == "seller":
            query = query.filter_by(seller_id=role_id).filter(
                Transactions.transaction_status != 1
            )

        if tx:
            query = query.filter_by(id=tx)
        if date == "newest":
            query = query.order_by(self.transaction.created_at.desc())
        if date == "oldest":
            query = query.order_by(self.transaction.created_at.asc())
        if status:
            query = query.filter_by(transaction_status=status)

        return query.paginate(page=page, per_page=per_page)

    def get_transaction_by_parent_id(self, parent_id):
        return self.transaction.query.filter_by(parent_id=parent_id).all()

    def get_transaction_by_id(self, transaction_id, role, role_id):
        query = self.transaction.query.filter_by(id=transaction_id)

        if role == "user":
            query = query.filter_by(user_id=role_id)
        if role == "seller":
            query = query.filter_by(seller_id=role_id)

        return query.first()
