import frappe
from frappe import _
from frappe.model.document import Document


class FuelLog(Document):

    def validate(self):
        self.calculate_amount()
        self.fetch_previous_odometer()
        self.calculate_efficiency()

    def calculate_amount(self):
        self.total_amount = (self.quantity_litres or 0) * (self.rate_per_litre or 0)

    def fetch_previous_odometer(self):
        if self.vehicle and self.is_new():
            prev = frappe.db.get_value("Vehicle", self.vehicle, "current_odometer_km") or 0
            self.previous_odometer_km = prev

    def calculate_efficiency(self):
        if self.odometer_reading_km and self.previous_odometer_km:
            dist = self.odometer_reading_km - self.previous_odometer_km
            self.distance_since_last_fill = dist if dist > 0 else 0
            if self.quantity_litres and self.quantity_litres > 0 and dist > 0:
                self.fuel_efficiency_kmpl = dist / self.quantity_litres
            else:
                self.fuel_efficiency_kmpl = 0

    def on_submit(self):
        if self.vehicle and self.odometer_reading_km:
            frappe.db.set_value(
                "Vehicle", self.vehicle, "current_odometer_km", self.odometer_reading_km
            )
