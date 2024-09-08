from app.db import db
from .transactions_repository import TransactionsRepository
from .transactions_service import TransactionsService
from ..sellers.sellers_service import SellersServices
from ..users.users_services import UserServices
from ..products.products_services import ProductsServices
from ..product_orders.product_orders_service import ProductOrdersService
from ..shipment_details.shipment_details_service import ShipmentDetailsService


class TransactionsDeleteRead:
    def __init__(
        self,
        db=db,
        repository=None,
        transaction_service=None,
        seller_service=None,
        user_service=None,
        product_serivce=None,
        product_order_service=None,
        shipment_detail_service=None,
    ):
        self.db = db
        self.repository = repository or TransactionsRepository()
        self.transaction_service = transaction_service or TransactionsService()
        self.seller_service = seller_service or SellersServices()
        self.user_service = user_service or UserServices()
        self.product_service = product_serivce or ProductsServices()
        self.product_order_service = product_order_service or ProductOrdersService()
        self.shipment_detail_service = (
            shipment_detail_service or ShipmentDetailsService()
        )

    def list_transactions(self, identity, req):
        try:
            tx = req.args.get("tx", None)
            date = req.args.get("date", None)
            page = req.args.get("page", 1, int)
            per_page = req.args.get("per_page", 10, int)
            status = req.args.get("status", None, int)
            role = identity.get("role")
            role_id = identity.get("id")

            self.check_role(identity=identity)

            transactions = self.repository.get_transaction_by_user_id(
                role=role,
                role_id=role_id,
                tx=tx,
                date=date,
                page=page,
                per_page=per_page,
                status=status,
            )

            if not transactions:
                raise ValueError("No transactions found")

            return self.response(transactions), 200

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def cancel_transaction(self, identity, transaction_id):
        try:
            self.check_role(identity=identity)
            role = identity.get("role")
            role_id = identity.get("id")

            transaction = self.repository.get_transaction_by_id(
                transaction_id=transaction_id, role=role, role_id=role_id
            )

            if not transaction:
                raise ValueError("Transaction not found")

            if role == "user":
                self.canceled_by_user(transaction=transaction)
            if role == "seller":
                self.canceled_by_seller(transaction=transaction)

            delete_shipment_detail, status_code = (
                self.shipment_detail_service.delete_detail(
                    transaction_id=transaction_id
                )
            )

            if status_code != 200:
                raise ValueError(
                    f"{delete_shipment_detail['error']} while trying to delete shipment detail"
                )

            self.db.session.commit()
            return {"message": "Transaction canceled successfully"}, 200

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def check_role(self, identity):
        role = identity.get("role")
        role_id = identity.get("id")

        if role == "seller":
            detail, status_code = self.seller_service.seller_info(seller_id=role_id)
        if role == "user":
            detail, status_code = self.user_service.user_info(user_id=role_id)

        if status_code != 200:
            raise ValueError(detail["error"])

    def response(self, transactions):
        return {
            "transactions": [transaction.to_dict() for transaction in transactions],
            "total_page": transactions.pages,
            "current_page": transactions.page,
            "total_items": transactions.total,
        }

    def canceled_by_user(self, transaction, role="user"):
        status = transaction.transaction_status
        if status == 1:
            transaction.canceled_transaction(role=role)

        if status == 2:
            transaction.canceled_transaction(role=role)
            transaction_gross_amount = transaction.gross_amount
            user_id = transaction.user_id

            self.refund_user(user_id=user_id, amount=transaction_gross_amount)
            self.product_cancelled_modification(transaction_id=transaction.id)

        if status == 3:
            raise ValueError(
                "Items are being prepared by seller, please contact seller to cancel the transaction"
            )

        if status == 4:
            raise ValueError("Items on delivery. Transaction can't be canceled")

        if status == 5:
            raise ValueError("Items delivered. Transaction can't be canceled")

        if status == 6:
            raise ValueError("Transaction has been canceled.")

    def canceled_by_seller(self, transaction, role="seller"):
        status = transaction.transaction_status
        if status == 1:
            raise ValueError("Seller can't cancel an unpaid transaction")
        if status in [2, 3]:
            transaction.canceled_transaction(role=role)
            transaction_gross_amount = transaction.gross_amount
            user_id = transaction.user_id

            self.refund_user(user_id=user_id, amount=transaction_gross_amount)
            self.product_cancelled_modification(transaction_id=transaction.id)

        if status == 4:
            raise ValueError("Items on delivery. Transaction can't be canceled")

        if status == 5:
            raise ValueError("Items delivered. Transaction can't be canceled")

        if status == 6:
            raise ValueError("Transaction has been canceled.")

    def refund_user(self, user_id, amount):
        message, status_code = self.user_service.refund(
            user_id=user_id, amount=amount, commit=False
        )

        if status_code != 200:
            raise ValueError(
                f"{message['error']} while trying to refund balance to user"
            )

    def product_cancelled_modification(self, transaction_id):
        product_orders, status_code = (
            self.product_order_service.get_product_orders_by_transaction_id(
                transaction_id=transaction_id
            )
        )

        if status_code != 200:
            raise ValueError(product_orders["error"])

        for product in product_orders:
            product_id = product["product_id"]
            quantity = product["quantity"]

            message, status_code = (
                self.product_service.transaction_canceled_modification(
                    product_id=product_id, quantity=quantity, commit=False
                )
            )

            if status_code != 200:
                raise ValueError(message["error"])
