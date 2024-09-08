from flask import Blueprint

user_seller_vouchers_blueprint = Blueprint(
    "user_seller_vouchers_blueprint", __name__, url_prefix="/api/usersellervouchers"
)

from . import user_seller_vouchers_controller
