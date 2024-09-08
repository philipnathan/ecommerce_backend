from app.db import db
from .transactions_repository import TransactionsRepository
from app.models.transactions import transaction_status
from ..midtrans.midtrans_service import MidtransService
from ..payment_details.payment_details_service import PaymentDetailsService
from ..product_orders.product_orders_service import ProductOrdersService
from ..products.products_services import ProductsServices
from .transactions_voucher import TransactionsVoucherService
from ..shipment_details.shipment_details_service import ShipmentDetailsService


class MidtransConfirmation:
    def __init__(
        self,
        db=db,
        repository=None,
        midtrans_service=None,
        payment_details_service=None,
        product_order_service=None,
        product_service=None,
        transaction_voucher_service=None,
        shipment_detail_service=None,
    ):
        self.db = db
        self.repository = repository or TransactionsRepository()
        self.midtrans_service = midtrans_service or MidtransService()
        self.payment_details_service = (
            payment_details_service or PaymentDetailsService()
        )
        self.product_order_service = product_order_service or ProductOrdersService()
        self.product_service = product_service or ProductsServices()
        self.transaction_voucher_service = (
            transaction_voucher_service or TransactionsVoucherService()
        )
        self.shipment_detail_service = (
            shipment_detail_service or ShipmentDetailsService()
        )

    def midtrans_confirmation(self, data):
        try:
            # raise valueerror
            message, status_code = self.midtrans_service.webhook(data)

            if status_code != 200:
                raise ValueError(message["error"])

            new_payment_details = self.payment_details_service.input_details(data)[0][
                "details"
            ]

            payment_details_id = new_payment_details.to_dict()["id"]

            transactions = self.repository.get_transaction_by_parent_id(
                data["order_id"]
            )

            # if failed, cancel all transaction
            if data["transaction_status"] in ["expire", "deny", "cancel"]:

                for transaction in transactions:
                    transaction.transaction_status = transaction_status.CANCELED.value

                    transaction.payment_details_id = payment_details_id
                    transaction.payment_link = None

                    # unused voucher
                    if transaction.user_seller_voucher_id:
                        unused, status_code = self.unused_voucher(
                            transaction=transaction
                        )

                        if status_code != 200:
                            raise ValueError(f"{unused['error']} while unused voucher")

                    delete_shipment_detail, status_code = (
                        self.shipment_detail_service.delete_detail(
                            transaction_id=transaction.id
                        )
                    )

                    if status_code != 200:
                        raise ValueError(
                            f"{delete_shipment_detail['error']} while deleting shipment detail"
                        )

            elif data["transaction_status"] == "settlement":
                for transaction in transactions:

                    # if already success, to prevent multiple success and multiple of reducing stock
                    if transaction.transaction_status in [
                        transaction_status.PAYMENT_SUCCESS.value,
                    ]:
                        continue

                    transaction.transaction_status = (
                        transaction_status.PAYMENT_SUCCESS.value
                    )

                    transaction.payment_details_id = payment_details_id
                    transaction.payment_link = None

                    message, status_code = self.reduce_quantity(
                        transaction_id=transaction.id, commit=False
                    )

                    if status_code != 200:
                        raise ValueError(message["error"])
            else:
                for transaction in transactions:
                    transaction.payment_details_id = payment_details_id

            self.db.session.commit()

            return {"success": True}, 200

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def reduce_quantity(self, transaction_id, commit=True):
        try:
            product_orders, status_code = (
                self.product_order_service.get_product_orders_by_transaction_id(
                    transaction_id=transaction_id
                )
            )

            if status_code != 200:
                raise ValueError(product_orders["error"])

            for product in product_orders:
                message, status_code = (
                    self.product_service.transaction_success_modification(
                        product_id=product["product_id"],
                        quantity=product["quantity"],
                        commit=False,
                    )
                )

            if status_code != 200:
                raise ValueError(message)
            if commit:
                self.db.session.commit()
            return {"success": True}, 200

        except ValueError as e:
            if commit:
                self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            if commit:
                self.db.session.rollback()
            return {"error": str(e)}, 500

    def unused_voucher(self, transaction):
        try:
            user_seller_voucher_id = transaction.user_seller_voucher_id
            user_id = transaction.user_id

            unused, status_code = (
                self.transaction_voucher_service.unused_user_seller_voucher(
                    user_id=user_id, user_seller_voucher_id=user_seller_voucher_id
                )
            )

            if status_code != 200:
                raise ValueError(unused["error"])

            return {"success": True}, 200

        except Exception as e:
            return {"error": str(e)}, 500
