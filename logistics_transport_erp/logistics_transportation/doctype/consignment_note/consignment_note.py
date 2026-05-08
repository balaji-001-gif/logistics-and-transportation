import frappe
from frappe import _
from frappe.model.document import Document


class ConsignmentNote(Document):

    def validate(self):
        self.calculate_totals()
        self.fetch_from_freight_order()

    def on_submit(self):
        self.db_set("status", "In Transit")

    def on_cancel(self):
        self.db_set("status", "Cancelled")

    def calculate_totals(self):
        total_packages = 0
        total_weight = 0.0
        for row in (self.goods_items or []):
            total_packages += row.packages or 0
            total_weight += row.weight_kg or 0
        self.total_packages = total_packages
        self.total_weight_kg = total_weight

    def fetch_from_freight_order(self):
        if self.freight_order and not self.vehicle:
            fo = frappe.get_doc("Freight Order", self.freight_order)
            self.vehicle = fo.vehicle
            self.driver = fo.driver
            if fo.origin_warehouse:
                self.origin_city = frappe.db.get_value(
                    "Warehouse", fo.origin_warehouse, "city"
                ) or ""
            if fo.destination_warehouse:
                self.destination_city = frappe.db.get_value(
                    "Warehouse", fo.destination_warehouse, "city"
                ) or ""
