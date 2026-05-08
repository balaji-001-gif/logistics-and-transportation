import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class StockTransferOrder(Document):

    def validate(self):
        self.validate_warehouses()
        self.calculate_totals()

    def on_submit(self):
        self.db_set("status", "In Transit")

    def on_cancel(self):
        self.db_set("status", "Cancelled")

    def validate_warehouses(self):
        if self.from_warehouse and self.to_warehouse:
            if self.from_warehouse == self.to_warehouse:
                frappe.throw(_("From Warehouse and To Warehouse cannot be the same."))

    def calculate_totals(self):
        total_qty = 0.0
        total_val = 0.0
        for row in (self.items or []):
            total_qty += flt(row.quantity)
            total_val += flt(row.quantity) * flt(row.unit_value)
        self.total_quantity = total_qty
        self.total_value = total_val
        if self.gst_applicable:
            self.cgst_amount = total_val * 0.09
            self.sgst_amount = total_val * 0.09
            self.igst_amount = 0
            self.grand_total = total_val + self.cgst_amount + self.sgst_amount
        else:
            self.cgst_amount = 0
            self.sgst_amount = 0
            self.igst_amount = 0
            self.grand_total = total_val
