import frappe
from frappe import _
from frappe.model.document import Document


class Pod(Document):

    def validate(self):
        self.update_freight_order()

    def update_freight_order(self):
        if self.freight_order and self.status == "Delivered":
            frappe.db.set_value("Freight Order", self.freight_order, {
                "status": "Delivered",
                "actual_delivery_date": self.delivery_datetime
            })
