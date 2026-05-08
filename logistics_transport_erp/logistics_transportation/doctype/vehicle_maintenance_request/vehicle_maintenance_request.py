import frappe
from frappe import _
from frappe.model.document import Document


class VehicleMaintenanceRequest(Document):

    def validate(self):
        self.calculate_costs()

    def on_submit(self):
        self.db_set("status", "Completed")
        self.update_vehicle_service_record()

    def on_cancel(self):
        self.db_set("status", "Cancelled")

    def calculate_costs(self):
        total_parts = sum(
            (row.quantity or 0) * (row.unit_cost or 0)
            for row in (self.parts_used or [])
        )
        for row in (self.parts_used or []):
            row.total_cost = (row.quantity or 0) * (row.unit_cost or 0)
        self.total_parts_cost = total_parts
        self.total_maintenance_cost = total_parts + (self.labour_cost or 0)

    def update_vehicle_service_record(self):
        if self.vehicle and self.completed_date:
            frappe.db.set_value("Vehicle", self.vehicle, {
                "last_service_km": self.odometer_at_request_km or 0
            })
