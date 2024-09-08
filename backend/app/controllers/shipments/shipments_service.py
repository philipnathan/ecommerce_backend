from app.db import db
from .shipments_repository import ShipmentsRepository


class ShipmentsService:

    def __init__(self, db=db, repository=None):
        self.db = db
        self.repository = repository or ShipmentsRepository()

    def list_shipments(self):
        try:
            shipments = self.repository.get_list_shipments()
            return [shipment.to_dict() for shipment in shipments]
        except Exception as e:
            return {"error": str(e)}, 500
