import frappe
from frappe import _
from frappe.utils import flt, date_diff, getdate


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
        {"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Link", "options": "Vehicle", "width": 140},
        {"label": _("Vehicle Type"), "fieldname": "vehicle_type", "fieldtype": "Link", "options": "Vehicle Type", "width": 140},
        {"label": _("Total Trips"), "fieldname": "total_trips", "fieldtype": "Int", "width": 100},
        {"label": _("Active Days"), "fieldname": "active_days", "fieldtype": "Int", "width": 100},
        {"label": _("Total KM"), "fieldname": "total_km", "fieldtype": "Float", "width": 100},
        {"label": _("Avg KM/Day"), "fieldname": "avg_km_day", "fieldtype": "Float", "width": 110},
        {"label": _("Total Fuel (L)"), "fieldname": "total_fuel", "fieldtype": "Float", "width": 120},
        {"label": _("Avg Efficiency (km/l)"), "fieldname": "avg_efficiency", "fieldtype": "Float", "width": 160},
        {"label": _("Load Factor %"), "fieldname": "avg_load_factor", "fieldtype": "Percent", "width": 120},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
    ]


def get_data(filters):
    conditions = "WHERE ts.docstatus = 1"
    if filters.get("from_date"):
        conditions += " AND ts.trip_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND ts.trip_date <= %(to_date)s"
    if filters.get("vehicle_type"):
        conditions += " AND v.vehicle_type = %(vehicle_type)s"

    vehicles = frappe.db.sql(f"""
        SELECT
            v.name as vehicle,
            v.vehicle_type,
            v.status,
            COUNT(ts.name) as total_trips,
            COUNT(DISTINCT ts.trip_date) as active_days,
            SUM(ts.distance_covered_km) as total_km,
            SUM(ts.total_fuel_litres) as total_fuel
        FROM `tabVehicle` v
        LEFT JOIN `tabTrip Sheet` ts ON ts.vehicle = v.name {conditions.replace('WHERE', 'AND')}
        GROUP BY v.name
        ORDER BY total_trips DESC
    """, filters, as_dict=True)

    result = []
    for v in vehicles:
        total_km = flt(v.total_km)
        active_days = v.active_days or 0
        total_fuel = flt(v.total_fuel)

        result.append({
            "vehicle": v.vehicle,
            "vehicle_type": v.vehicle_type,
            "total_trips": v.total_trips or 0,
            "active_days": active_days,
            "total_km": total_km,
            "avg_km_day": total_km / active_days if active_days else 0,
            "total_fuel": total_fuel,
            "avg_efficiency": total_km / total_fuel if total_fuel else 0,
            "avg_load_factor": 0,
            "status": v.status,
        })

    return result
