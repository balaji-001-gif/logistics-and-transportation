import frappe
from frappe import _
from frappe.model.document import Document


class RouteMaster(Document):

    def validate(self):
        if self.origin_city and self.destination_city:
            if self.origin_city.strip().lower() == self.destination_city.strip().lower():
                frappe.throw(_("Origin and Destination cities cannot be the same."))

        if not self.route_name:
            self.route_name = f"{self.origin_city} - {self.destination_city}"
