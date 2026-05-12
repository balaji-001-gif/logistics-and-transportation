"""
Driver Portal API
=================
Provides endpoints for the Driver Mobile Web Portal.
Requires User to be linked to a 'Driver' document.
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, today


@frappe.whitelist()
def get_driver_info():
    """Returns basic info about the logged-in driver."""
    driver = _get_current_driver()
    return {
        "name":      driver.full_name,
        "id":        driver.name,
        "vehicle":   driver.get("current_vehicle"),
        "status":    driver.status,
    }


@frappe.whitelist()
def get_assigned_trips():
    """Returns 'Open' and 'In Transit' Trip Sheets for the driver."""
    driver = _get_current_driver()
    trips = frappe.get_all(
        "Trip Sheet",
        filters={"driver": driver.name, "status": ["in", ["Open", "In Transit"]]},
        fields=["name", "trip_date", "status", "vehicle", "start_odometer_km"],
        order_by="trip_date desc"
    )
    return trips


@frappe.whitelist()
def update_trip_status(trip_name, event_type, lat=None, lng=None, remarks=None):
    """Adds a Tracking Event and updates Trip status."""
    driver = _get_current_driver()
    trip   = frappe.get_doc("Trip Sheet", trip_name)
    
    if trip.driver != driver.name:
        frappe.throw(_("Unauthorized: You are not the assigned driver for this trip."))

    # Get freight orders associated with this trip
    lp = frappe.get_doc("Load Plan", trip.load_plan)
    for order_row in lp.freight_orders:
        event = frappe.get_doc({
            "doctype":          "Shipment Tracking Event",
            "freight_order":    order_row.freight_order,
            "event_type":       event_type,
            "event_datetime":   now_datetime(),
            "latitude":         lat,
            "longitude":        lng,
            "updated_by_driver": driver.name,
            "remarks":          remarks
        })
        event.insert(ignore_permissions=True)

    if event_type == "Dispatched" and trip.status == "Open":
        trip.db_set("status", "In Transit")
        trip.db_set("departure_time", now_datetime())
    
    return {"status": "success", "message": _("Status updated successfully")}


@frappe.whitelist()
def log_expense(trip_name, expense_type, amount, details=None):
    """Logs Toll or Fuel expense from the portal."""
    driver = _get_current_driver()
    trip   = frappe.get_doc("Trip Sheet", trip_name)

    if expense_type == "Toll":
        trip.append("toll_entries", {
            "toll_location": details or "Via Portal",
            "date":          today(),
            "amount":        float(amount)
        })
    elif expense_type == "Fuel":
        trip.append("fuel_entries", {
            "fuel_station": details or "Via Portal",
            "date":         today(),
            "quantity_litres": 0, # could add this to UI later
            "rate_per_litre": 0,
            "amount":       float(amount)
        })
    
    trip.save(ignore_permissions=True)
    return {"status": "success"}


def _get_current_driver():
    """Helper to find Driver doc linked to current User."""
    user = frappe.session.user
    driver_name = frappe.db.get_value("Driver", {"employee": frappe.db.get_value("Employee", {"user_id": user}, "name")}, "name")
    if not driver_name:
        # Fallback to direct user link if employee link is missing
        driver_name = frappe.db.get_value("Driver", {"full_name": frappe.user.full_name}, "name")
    
    if not driver_name:
        frappe.throw(_("User is not linked to any Driver record. Please contact administrator."), frappe.PermissionError)
    
    return frappe.get_doc("Driver", driver_name)
