import frappe
from frappe import _
from frappe.model.document import Document


class LoadPlan(Document):

    def validate(self):
        self.calculate_load_totals()
        self.fetch_vehicle_capacity()

    def on_submit(self):
        self.db_set("status", "Confirmed")

    def on_cancel(self):
        self.db_set("status", "Cancelled")

    def calculate_load_totals(self):
        total_weight = 0.0
        total_volume = 0.0
        for row in (self.freight_orders or []):
            total_weight += row.total_weight_kg or 0
            total_volume += row.total_volume_cbm or 0
        self.total_weight_kg = total_weight
        self.total_volume_cbm = total_volume

    def fetch_vehicle_capacity(self):
        if self.vehicle:
            capacity = frappe.db.get_value(
                "Vehicle", self.vehicle, "payload_capacity_kg"
            ) or 0
            self.vehicle_capacity_kg = capacity
            if capacity > 0:
                self.load_factor_percent = (self.total_weight_kg / capacity) * 100
            else:
                self.load_factor_percent = 0

            if self.load_factor_percent > 100:
                frappe.msgprint(
                    _("Warning: Load factor {0:.1f}% exceeds vehicle capacity.").format(
                        self.load_factor_percent
                    ),
                    alert=True, indicator="red"
                )
