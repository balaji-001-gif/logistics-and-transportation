import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class OutboundShipment(Document):

    def validate(self):
        self.calculate_totals()

    def on_submit(self):
        self.db_set("status", "Dispatched")

    def on_cancel(self):
        self.db_set("status", "Cancelled")

    def calculate_totals(self):
        total_ordered = 0.0
        total_picked = 0.0
        total_packed = 0.0
        for row in (self.items or []):
            total_ordered += flt(row.ordered_qty)
            total_picked += flt(row.picked_qty)
            total_packed += flt(row.packed_qty)
        self.total_ordered_qty = total_ordered
        self.total_picked_qty = total_picked
        self.total_packed_qty = total_packed
