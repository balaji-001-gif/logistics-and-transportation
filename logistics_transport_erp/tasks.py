"""
Scheduled Background Tasks
===========================
All scheduler-triggered functions live here.

Registered in hooks.py:
    scheduler_events = {
        "daily": [
            "logistics_transport_erp.tasks.auto_maintenance_check",
            "logistics_transport_erp.tasks.check_ewb_expiry",
        ]
    }
"""

import frappe
from frappe import _
from frappe.utils import getdate, today, add_days, date_diff


# ─────────────────────────────────────────────────────────────────
# Feature 3 — Predictive Maintenance Scheduler
# ─────────────────────────────────────────────────────────────────

def auto_maintenance_check():
    """
    Daily job: scans all active vehicles for impending service dues.

    Triggers:
      1. current_odometer_km >= (next_service_km - alert_km_threshold)
      2. today >= (next_service_date - alert_days_threshold)

    When triggered:
      - Creates a 'Vehicle Maintenance Request' if one doesn't already exist.
      - Stamps 'maintenance_alert_sent_on' to avoid duplicate alerts today.
    """
    try:
        settings        = frappe.get_single("Logistics Settings")
        alert_days      = int(settings.maintenance_alert_days or 7)
        alert_km        = int(settings.maintenance_alert_km   or 500)
    except Exception:
        alert_days, alert_km = 7, 500

    vehicles = frappe.get_all(
        "Vehicle",
        filters={"status": ["in", ["Available", "On Trip"]]},
        fields=[
            "name", "registration_number",
            "current_odometer_km", "next_service_km", "next_service_date",
            "maintenance_alert_sent_on",
        ],
    )

    today_date = getdate(today())

    for v in vehicles:
        # Skip if we already alerted today
        if v.maintenance_alert_sent_on and getdate(v.maintenance_alert_sent_on) == today_date:
            continue

        reason = None

        # Check odometer threshold
        if v.current_odometer_km and v.next_service_km:
            km_remaining = v.next_service_km - v.current_odometer_km
            if km_remaining <= alert_km:
                reason = (
                    f"Odometer {v.current_odometer_km} km — service due at {v.next_service_km} km "
                    f"({km_remaining:.0f} km remaining)."
                )

        # Check date threshold (only if not already flagged)
        if not reason and v.next_service_date:
            days_remaining = date_diff(v.next_service_date, today_date)
            if days_remaining <= alert_days:
                reason = (
                    f"Service due on {v.next_service_date} "
                    f"({days_remaining} days remaining)."
                )

        if reason:
            _create_vmr_if_needed(v, reason)
            frappe.db.set_value("Vehicle", v.name, "maintenance_alert_sent_on", today_date)

    frappe.db.commit()


def _create_vmr_if_needed(vehicle, reason: str):
    """Creates a Vehicle Maintenance Request if no open one exists for this vehicle."""
    existing = frappe.db.exists(
        "Vehicle Maintenance Request",
        {"vehicle": vehicle.name, "status": ["in", ["Open", "In Progress"]]},
    )
    if existing:
        return  # Already an open VMR — no duplicate

    try:
        vmr = frappe.get_doc({
            "doctype":     "Vehicle Maintenance Request",
            "vehicle":     vehicle.name,
            "request_date": today(),
            "priority":    "High",
            "status":      "Open",
            "issue_description": f"[AUTO] Predictive Maintenance Alert\n\n{reason}",
        })
        vmr.insert(ignore_permissions=True)
        frappe.db.commit()

        _notify_fleet_manager(vehicle, vmr.name, reason)
        frappe.log_error(
            f"Auto-VMR created for {vehicle.registration_number}: {reason}",
            "Predictive Maintenance"
        )
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Predictive Maintenance VMR Creation")


def _notify_fleet_manager(vehicle, vmr_name: str, reason: str):
    """Sends an in-app notification to users with Fleet Manager role."""
    managers = frappe.get_all(
        "Has Role",
        filters={"role": "Fleet Manager", "parenttype": "User"},
        fields=["parent"],
    )
    for m in managers:
        frappe.publish_realtime(
            event="msgprint",
            message=_(
                "🔧 Predictive Maintenance: Vehicle {0} needs servicing soon.\n{1}\nVMR: {2}"
            ).format(vehicle.registration_number, reason, vmr_name),
            user=m.parent,
        )


# ─────────────────────────────────────────────────────────────────
# Feature 4 — E-Way Bill Expiry Check (daily)
# ─────────────────────────────────────────────────────────────────

def check_ewb_expiry():
    """
    Daily job: checks all active E-Way Bills for impending expiry
    and sends alerts based on ewb_expiry_alert_hours setting.
    """
    try:
        settings       = frappe.get_single("Logistics Settings")
        alert_hours    = int(settings.ewb_expiry_alert_hours or 6)
    except Exception:
        alert_hours = 6

    from frappe.utils import now_datetime, add_to_date
    now      = now_datetime()
    boundary = add_to_date(now, hours=alert_hours)

    expiring = frappe.get_all(
        "E Way Bill",
        filters={
            "status":     ["in", ["Generated", "Active"]],
            "valid_upto": ["between", [str(now), str(boundary)]],
        },
        fields=["name", "ewb_number", "valid_upto", "freight_order"],
    )

    for ewb in expiring:
        frappe.publish_realtime(
            event="msgprint",
            message=_(
                "⚠️ E-Way Bill {0} (EWB No: {1}) expires at {2}. Please extend or generate a new one."
            ).format(ewb.name, ewb.ewb_number or "N/A", ewb.valid_upto),
        )
