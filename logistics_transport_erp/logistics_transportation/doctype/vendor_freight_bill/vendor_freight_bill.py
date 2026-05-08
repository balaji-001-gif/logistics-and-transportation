import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class VendorFreightBill(Document):

    def validate(self):
        self.calculate_amounts()

    def on_submit(self):
        self.db_set("status", "Pending Approval")

    def on_cancel(self):
        self.db_set("status", "Cancelled")

    def calculate_amounts(self):
        base = flt(self.base_freight_amount)
        tds = base * (flt(self.tds_rate) / 100)
        self.tds_amount = tds
        self.net_payable = base - tds
        self.balance_due = self.net_payable - flt(self.amount_paid)
