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
        {"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Link", "options": "Vehicle", "width": 150},
        {"label": _("Revenue (Freight)"), "fieldname": "revenue", "fieldtype": "Currency", "width": 120},
        {"label": _("Fuel Expense"), "fieldname": "fuel_cost", "fieldtype": "Currency", "width": 120},
        {"label": _("Toll Expense"), "fieldname": "toll_cost", "fieldtype": "Currency", "width": 120},
        {"label": _("Maintenance Cost"), "fieldname": "maintenance_cost", "fieldtype": "Currency", "width": 140},
        {"label": _("Net Profit"), "fieldname": "profit", "fieldtype": "Currency", "width": 120},
        {"label": _("Margin %"), "fieldname": "margin_percent", "fieldtype": "Percent", "width": 100},
    ]


def get_data(filters):
    # Fetch all vehicles
    vehicles = frappe.get_all("Vehicle", fields=["name"])
    data = []

    for v in vehicles:
        # 1. Revenue from Freight Orders
        revenue = frappe.db.get_value(
            "Freight Order",
            {"vehicle": v.name, "docstatus": 1},
            "sum(total_amount)"
        ) or 0

        # 2. Costs from Trip Sheets
        costs = frappe.db.get_all(
            "Trip Sheet",
            filters={"vehicle": v.name, "docstatus": 1},
            fields=["sum(total_fuel_amount) as fuel", "sum(total_toll_amount) as toll"]
        )
        fuel_cost = costs[0].fuel if costs and costs[0].fuel else 0
        toll_cost = costs[0].toll if costs and costs[0].toll else 0

        # 3. Maintenance Costs
        maint_cost = frappe.db.get_value(
            "Vehicle Maintenance Request",
            {"vehicle": v.name, "status": "Completed"},
            "sum(maintenance_cost)" # Assuming this field exists or adding it
        ) or 0

        profit = revenue - (fuel_cost + toll_cost + maint_cost)
        margin = (profit / revenue * 100) if revenue > 0 else 0

        data.append({
            "vehicle":          v.name,
            "revenue":          revenue,
            "fuel_cost":        fuel_cost,
            "toll_cost":        toll_cost,
            "maintenance_cost": maint_cost,
            "profit":           profit,
            "margin_percent":   margin
        })

    return data
