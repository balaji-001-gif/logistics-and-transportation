import frappe
from frappe.model.document import Document
from frappe.utils import flt


class FreightSettlement(Document):

    def validate(self):
        self.calculate_profitability()

    def on_submit(self):
        self.db_set("status", "Submitted")

    def on_cancel(self):
        self.db_set("status", "Cancelled")

    def calculate_profitability(self):
        total_revenue = sum(flt(r.net_revenue) for r in (self.revenue_lines or []))
        total_cost = sum(flt(r.amount) for r in (self.cost_lines or []))
        self.total_revenue = total_revenue
        self.total_cost = total_cost
        self.gross_margin = total_revenue - total_cost
        self.margin_percent = (self.gross_margin / total_revenue * 100) if total_revenue else 0
