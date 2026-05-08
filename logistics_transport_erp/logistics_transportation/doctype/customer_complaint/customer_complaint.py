import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, today


class CustomerComplaint(Document):

    def validate(self):
        if self.freight_order and not self.customer:
            self.customer = frappe.db.get_value(
                "Freight Order", self.freight_order, "customer"
            )
        self.validate_claim()

    def validate_claim(self):
        if flt(self.approved_claim_amount) > flt(self.claim_amount):
            frappe.throw(
                _("Approved Claim Amount cannot exceed Claim Amount.")
            )
