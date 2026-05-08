import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
        {"label": _("Trip Sheet"), "fieldname": "trip_sheet", "fieldtype": "Link", "options": "Trip Sheet", "width": 140},
        {"label": _("Trip Date"), "fieldname": "trip_date", "fieldtype": "Date", "width": 100},
        {"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Link", "options": "Vehicle", "width": 130},
        {"label": _("Driver"), "fieldname": "driver", "fieldtype": "Link", "options": "Driver", "width": 130},
        {"label": _("Route"), "fieldname": "route", "fieldtype": "Data", "width": 160},
        {"label": _("Revenue (INR)"), "fieldname": "revenue", "fieldtype": "Currency", "width": 130},
        {"label": _("Fuel Cost (INR)"), "fieldname": "fuel_cost", "fieldtype": "Currency", "width": 130},
        {"label": _("Toll Cost (INR)"), "fieldname": "toll_cost", "fieldtype": "Currency", "width": 130},
        {"label": _("Total Cost (INR)"), "fieldname": "total_cost", "fieldtype": "Currency", "width": 130},
        {"label": _("Gross Margin (INR)"), "fieldname": "gross_margin", "fieldtype": "Currency", "width": 140},
        {"label": _("Margin %"), "fieldname": "margin_pct", "fieldtype": "Percent", "width": 90},
    ]


def get_data(filters):
    conditions = "WHERE ts.docstatus = 1"
    if filters.get("from_date"):
        conditions += " AND ts.trip_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND ts.trip_date <= %(to_date)s"
    if filters.get("vehicle"):
        conditions += " AND ts.vehicle = %(vehicle)s"
    if filters.get("driver"):
        conditions += " AND ts.driver = %(driver)s"

    trips = frappe.db.sql(f"""
        SELECT
            ts.name as trip_sheet,
            ts.trip_date,
            ts.vehicle,
            ts.driver,
            ts.load_plan,
            ts.total_fuel_amount as fuel_cost,
            ts.total_toll_amount as toll_cost
        FROM `tabTrip Sheet` ts
        {conditions}
        ORDER BY ts.trip_date DESC
    """, filters, as_dict=True)

    result = []
    for t in trips:
        revenue = flt(frappe.db.get_value(
            "Freight Settlement", {"trip_sheet": t.trip_sheet}, "total_revenue"
        ) or 0)

        route = ""
        if t.load_plan:
            warehouse = frappe.db.get_value("Load Plan", t.load_plan, "origin_warehouse")
            if warehouse:
                route = warehouse

        fuel = flt(t.fuel_cost)
        toll = flt(t.toll_cost)
        total_cost = fuel + toll
        margin = revenue - total_cost
        margin_pct = (margin / revenue * 100) if revenue else 0

        result.append({
            "trip_sheet": t.trip_sheet,
            "trip_date": t.trip_date,
            "vehicle": t.vehicle,
            "driver": t.driver,
            "route": route,
            "revenue": revenue,
            "fuel_cost": fuel,
            "toll_cost": toll,
            "total_cost": total_cost,
            "gross_margin": margin,
            "margin_pct": margin_pct,
        })

    return result
