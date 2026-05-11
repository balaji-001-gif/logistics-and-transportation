"""
Google Maps API utility for the Logistics ERP.
"""

import frappe


@frappe.whitelist()
def get_maps_api_key():
    """
    Returns the Google Maps API key for client-side use.
    Only returns it if maps are enabled in Logistics Settings.
    """
    settings = frappe.get_single("Logistics Settings")
    if not settings.maps_enabled:
        return {"api_key": ""}
    return {"api_key": settings.get_password("google_maps_api_key") or ""}


@frappe.whitelist()
def geocode_city(city_name):
    """
    Geocodes a city name to lat/lng using Google Maps Geocoding API.
    Returns {"lat": float, "lng": float} or None.
    """
    import requests

    settings = frappe.get_single("Logistics Settings")
    api_key  = settings.get_password("google_maps_api_key") or ""
    if not api_key:
        return None

    try:
        resp = requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={"address": city_name, "key": api_key},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == "OK":
            loc = data["results"][0]["geometry"]["location"]
            return {"lat": loc["lat"], "lng": loc["lng"]}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Maps Geocoding")

    return None


@frappe.whitelist()
def get_route_distance(origin, destination):
    """
    Calculates driving distance & duration between two city names using
    Google Maps Distance Matrix API.
    Returns {"distance_km": float, "duration_minutes": float} or None.
    """
    import requests

    settings = frappe.get_single("Logistics Settings")
    api_key  = settings.get_password("google_maps_api_key") or ""
    if not api_key:
        return None

    try:
        resp = requests.get(
            "https://maps.googleapis.com/maps/api/distancematrix/json",
            params={
                "origins":      origin,
                "destinations": destination,
                "mode":         "driving",
                "key":          api_key,
                "units":        "metric",
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == "OK":
            element = data["rows"][0]["elements"][0]
            if element.get("status") == "OK":
                return {
                    "distance_km":      round(element["distance"]["value"] / 1000, 2),
                    "duration_minutes": round(element["duration"]["value"] / 60, 1),
                }
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Maps Distance Matrix")

    return None
