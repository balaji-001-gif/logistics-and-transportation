import frappe
from frappe import _
from frappe.model.document import Document


class TripSheet(Document):

    def validate(self):
        self.calculate_distance()
        self.calculate_toll_totals()
        self.calculate_fuel_totals()
        self.calculate_driver_balance()

    def on_submit(self):
        self.check_compliance_before_dispatch()
        self.db_set("status", "Completed")
        self.update_vehicle_odometer()
        self.update_driver_status()

    def update_driver_status(self):
        """Update driver's current vehicle link."""
        if self.driver and self.vehicle:
            frappe.db.set_value("Driver", self.driver, "current_vehicle", self.vehicle)


    def check_compliance_before_dispatch(self):
        """Block trip submission if Vehicle RC or Driver DL failed Vahan/Sarathi verification."""
        settings = frappe.get_single("Logistics Settings")
        if not settings.vahan_api_enabled:
            return  # Validation not enforced when API is disabled

        if self.vehicle:
            rc_status = frappe.db.get_value("Vehicle", self.vehicle, "rc_status")
            if rc_status and rc_status not in ("Active", "API Disabled"):
                frappe.throw(
                    _("Vehicle {0} RC status is '{1}'. Please verify RC via Vahan before dispatching.").format(
                        self.vehicle, rc_status
                    )
                )

        if self.driver:
            dl_status = frappe.db.get_value("Driver", self.driver, "dl_verified_status")
            if dl_status and dl_status not in ("Active", "API Disabled"):
                frappe.throw(
                    _("Driver {0} DL status is '{1}'. Please verify DL via Sarathi before dispatching.").format(
                        self.driver, dl_status
                    )
                )


    def on_cancel(self):
        self.db_set("status", "Cancelled")

    def calculate_distance(self):
        if self.start_odometer_km and self.end_odometer_km:
            if self.end_odometer_km < self.start_odometer_km:
                frappe.throw(_("End Odometer cannot be less than Start Odometer."))
            self.distance_covered_km = self.end_odometer_km - self.start_odometer_km

    def calculate_toll_totals(self):
        self.total_toll_amount = sum(
            (row.amount or 0) for row in (self.toll_entries or [])
        )

    def calculate_fuel_totals(self):
        total_litres = sum((row.quantity_litres or 0) for row in (self.fuel_entries or []))
        total_amount = sum((row.amount or 0) for row in (self.fuel_entries or []))
        self.total_fuel_litres = total_litres
        self.total_fuel_amount = total_amount
        if total_litres > 0 and self.distance_covered_km:
            self.fuel_efficiency_kmpl = self.distance_covered_km / total_litres
        else:
            self.fuel_efficiency_kmpl = 0

    def calculate_driver_balance(self):
        given = self.driver_advance_given or 0
        spent = (self.total_toll_amount or 0) + (self.total_fuel_amount or 0)
        recovered = self.driver_advance_recovered or 0
        self.driver_balance = given - spent - recovered

    def update_vehicle_odometer(self):
        if self.vehicle and self.end_odometer_km:
            frappe.db.set_value(
                "Vehicle", self.vehicle, "current_odometer_km", self.end_odometer_km
            )
