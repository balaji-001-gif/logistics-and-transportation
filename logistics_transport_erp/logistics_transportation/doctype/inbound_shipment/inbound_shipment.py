import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class InboundShipment(Document):

    def validate(self):
        self.calculate_totals()

    def on_submit(self):
        self.db_set("status", "Received")

    def on_cancel(self):
        self.db_set("status", "Cancelled")

    def calculate_totals(self):
        total_expected = 0.0
        total_received = 0.0
        damage_count = 0
        for row in (self.items or []):
            total_expected += flt(row.expected_qty)
            total_received += flt(row.received_qty)
            if row.is_damaged:
                damage_count += 1
        self.total_expected_qty = total_expected
        self.total_received_qty = total_received
        self.shortage_qty = max(0, total_expected - total_received)
        self.damage_count = damage_count
