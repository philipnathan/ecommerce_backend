from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from

from . import transactions_blueprint
from .transactions_service import TransactionsService
from .transactions_midtrans import MidtransConfirmation
from .transactions_service_read_delete import TransactionsDeleteRead
from .transactions_service_update import TransactionServiceUpdate

service = TransactionsService()
read_delete_service = TransactionsDeleteRead()
midtrans_confirmation = MidtransConfirmation()
update_service = TransactionServiceUpdate()


@transactions_blueprint.route("/create", methods=["POST"])
@jwt_required()
@swag_from("./transactions_create.yml")
def transaction_create():
    data = request.get_json()
    identity = get_jwt_identity()
    return service.create_transaction(data, identity)


@transactions_blueprint.route("/", methods=["GET"])
@jwt_required()
@swag_from("./transactions_get_list.yml")
def transaction_list():
    identity = get_jwt_identity()
    req = request
    return read_delete_service.list_transactions(identity, req)


@transactions_blueprint.route("/confirmation", methods=["POST"])
def midtrans_webhook():
    data = request.get_json()
    return midtrans_confirmation.midtrans_confirmation(data)


@transactions_blueprint.route("/cancel/<transaction_id>", methods=["POST"])
@jwt_required()
@swag_from("./transactions_cancel.yml")
def cancel_transaction(transaction_id):
    identity = get_jwt_identity()
    return read_delete_service.cancel_transaction(
        transaction_id=transaction_id, identity=identity
    )


@transactions_blueprint.route("/prepared/<transaction_id>", methods=["PUT"])
@jwt_required()
@swag_from("./transaction_prepared.yml")
def update_transaction(transaction_id):
    identity = get_jwt_identity()
    return update_service.change_to_prepared(
        identity=identity, transaction_id=transaction_id
    )


@transactions_blueprint.route("/ondelivery/<transaction_id>", methods=["PUT"])
@jwt_required()
@swag_from("./transaction_ondelivery.yml")
def update_transaction_ondelivery(transaction_id):
    identity = get_jwt_identity()
    data = request.get_json()
    return update_service.update_tracking_number(
        identity=identity, transaction_id=transaction_id, data=data
    )


@transactions_blueprint.route("/delivered/<transaction_id>", methods=["PUT"])
@jwt_required()
@swag_from("./transaction_delivered.yml")
def update_transaction_delivered(transaction_id):
    identity = get_jwt_identity()
    return update_service.update_to_delivered(
        identity=identity, transaction_id=transaction_id
    )


@transactions_blueprint.route("/review/<transaction_id>", methods=["POST"])
@jwt_required()
@swag_from("./transaction_review.yml")
def create_review(transaction_id):
    data = request.get_json()
    identity = get_jwt_identity()
    return update_service.create_review(
        data=data, transaction_id=transaction_id, identity=identity
    )
