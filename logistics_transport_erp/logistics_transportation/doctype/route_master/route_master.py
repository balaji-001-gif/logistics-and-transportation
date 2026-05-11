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

    def fetch_coordinates_from_api(self):
        """Geocodes origin & destination cities and fetches driving distance via Maps API."""
        from logistics_transport_erp.api.maps_api import geocode_city, get_route_distance

        if self.origin_city:
            origin_geo = geocode_city(self.origin_city)
            if origin_geo:
                self.db_set("lat_origin", origin_geo["lat"], notify=True)
                self.db_set("lng_origin", origin_geo["lng"], notify=True)

        if self.destination_city:
            dest_geo = geocode_city(self.destination_city)
            if dest_geo:
                self.db_set("lat_destination", dest_geo["lat"], notify=True)
                self.db_set("lng_destination", dest_geo["lng"], notify=True)

        if self.origin_city and self.destination_city:
            dist = get_route_distance(self.origin_city, self.destination_city)
            if dist:
                self.db_set("distance_km", dist["distance_km"], notify=True)
                transit_days = max(1, round(dist["duration_minutes"] / (60 * 8)))  # assume 8h driving/day
                self.db_set("estimated_transit_days", transit_days, notify=True)

        return {
            "lat_origin":         self.lat_origin,
            "lng_origin":         self.lng_origin,
            "lat_destination":    self.lat_destination,
            "lng_destination":    self.lng_destination,
            "distance_km":        self.distance_km,
            "estimated_transit_days": self.estimated_transit_days,
        }


@frappe.whitelist()
def fetch_route_coordinates(route_name):
    """Whitelisted endpoint for the 'Fetch Coordinates & Distance' button."""
    doc = frappe.get_doc("Route Master", route_name)
    return doc.fetch_coordinates_from_api()
