import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class ShipmentTrackingEvent(Document):

    def validate(self):
        if not self.event_datetime:
            self.event_datetime = now_datetime()
        self.update_freight_order_status()
        self.reverse_geocode_if_needed()

    def update_freight_order_status(self):
        status_map = {
            "Dispatched":       "Dispatched",
            "Delivered":        "Delivered",
            "In Transit":       "In Transit",
            "At Hub":           "In Transit",
            "Out for Delivery": "In Transit",
        }
        new_status = status_map.get(self.event_type)
        if new_status and self.freight_order:
            current = frappe.db.get_value("Freight Order", self.freight_order, "status")
            if current not in ("Delivered", "Cancelled"):
                frappe.db.set_value("Freight Order", self.freight_order, "status", new_status)

    def reverse_geocode_if_needed(self):
        """If GPS coordinates are set but city is empty, reverse geocode via Maps API."""
        if not (self.latitude and self.longitude):
            return
        if self.city:
            return  # already filled

        import requests
        try:
            settings = frappe.get_single("Logistics Settings")
            api_key  = settings.get_password("google_maps_api_key") or ""
            if not api_key:
                return
            resp = requests.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={
                    "latlng": f"{self.latitude},{self.longitude}",
                    "key":    api_key,
                    "result_type": "locality|administrative_area_level_1",
                },
                timeout=8,
            )
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") == "OK" and data.get("results"):
                components = data["results"][0].get("address_components", [])
                for comp in components:
                    if "locality" in comp["types"]:
                        self.city = comp["long_name"]
                    if "administrative_area_level_1" in comp["types"]:
                        self.state = comp["long_name"]
                if not self.location_description:
                    self.location_description = data["results"][0].get("formatted_address", "")
        except Exception:
            frappe.log_error(frappe.get_traceback(), "Reverse Geocode Tracking Event")
