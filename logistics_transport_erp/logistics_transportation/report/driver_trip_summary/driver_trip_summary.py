# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": _("Driver"), "fieldname": "driver", "fieldtype": "Link", "options": "Driver", "width": 150},
        {"label": _("Total Trips"), "fieldname": "total_trips", "fieldtype": "Int", "width": 100},
        {"label": _("Total KM Covered"), "fieldname": "total_km", "fieldtype": "Float", "width": 140},
        {"label": _("Total Fuel (L)"), "fieldname": "total_fuel", "fieldtype": "Float", "width": 120},
        {"label": _("Avg KMPL"), "fieldname": "avg_kmpl", "fieldtype": "Float", "width": 100},
        {"label": _("Advance Taken"), "fieldname": "advance", "fieldtype": "Currency", "width": 120},
    ]


def get_data(filters):
    drivers = frappe.get_all("Driver", fields=["name"])
    data = []

    for d in drivers:
        trips = frappe.get_all(
            "Trip Sheet",
            filters={"driver": d.name, "docstatus": 1},
            fields=[
                "count(name) as count",
                "sum(distance_covered_km) as km",
                "sum(total_fuel_litres) as fuel",
                "sum(driver_advance_given) as advance"
            ]
        )
        
        t = trips[0] if trips else None
        count = t.count if t and t.count else 0
        km    = t.km    if t and t.km    else 0
        fuel  = t.fuel  if t and t.fuel  else 0
        adv   = t.advance if t and t.advance else 0
        
        kmpl = (km / fuel) if fuel > 0 else 0

        data.append({
            "driver":      d.name,
            "total_trips": count,
            "total_km":    km,
            "total_fuel":  fuel,
            "avg_kmpl":    round(kmpl, 2),
            "advance":     adv
        })

    return data
