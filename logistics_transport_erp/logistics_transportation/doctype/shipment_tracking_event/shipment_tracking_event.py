import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class ShipmentTrackingEvent(Document):

    def validate(self):
        if not self.event_datetime:
            self.event_datetime = now_datetime()
        self.update_freight_order_status()

    def update_freight_order_status(self):
        status_map = {
            "Dispatched": "Dispatched",
            "Delivered": "Delivered",
            "In Transit": "In Transit",
            "At Hub": "In Transit",
            "Out for Delivery": "In Transit",
        }
        new_status = status_map.get(self.event_type)
        if new_status and self.freight_order:
            current = frappe.db.get_value("Freight Order", self.freight_order, "status")
            if current not in ("Delivered", "Cancelled"):
                frappe.db.set_value("Freight Order", self.freight_order, "status", new_status)
