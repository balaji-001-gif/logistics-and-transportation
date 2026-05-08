import frappe
from frappe.model.document import Document


class TollAndDetentionCharge(Document):

    def validate(self):
        if self.freight_order and not self.customer:
            self.customer = frappe.db.get_value(
                "Freight Order", self.freight_order, "customer"
            )
