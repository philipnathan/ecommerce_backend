from flask import Blueprint


seller_vouchers_blueprint = Blueprint(
    "seller_vouchers_blueprint", __name__, url_prefix="/api/sellervouchers"
)

from . import seller_vouchers_controller
