import frappe
from frappe.model.document import Document
from frappe.utils import flt


class AdvancePaymentRequest(Document):

    def validate(self):
        self.balance_outstanding = flt(self.amount_disbursed) - flt(self.amount_recovered)

    def on_submit(self):
        self.db_set("status", "Pending Approval")

    def on_cancel(self):
        self.db_set("status", "Cancelled")
