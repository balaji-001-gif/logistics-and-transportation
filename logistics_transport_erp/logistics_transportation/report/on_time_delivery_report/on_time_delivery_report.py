import frappe
from frappe import _
from frappe.utils import flt, getdate


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
        {"label": _("Freight Order"), "fieldname": "name", "fieldtype": "Link", "options": "Freight Order", "width": 150},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("Route"), "fieldname": "route", "fieldtype": "Link", "options": "Route Master", "width": 150},
        {"label": _("Driver"), "fieldname": "driver", "fieldtype": "Link", "options": "Driver", "width": 130},
        {"label": _("Expected Delivery"), "fieldname": "expected_delivery_date", "fieldtype": "Date", "width": 140},
        {"label": _("Actual Delivery"), "fieldname": "actual_delivery_date", "fieldtype": "Date", "width": 130},
        {"label": _("Delay (Days)"), "fieldname": "delay_days", "fieldtype": "Int", "width": 110},
        {"label": _("Status"), "fieldname": "delivery_status", "fieldtype": "Data", "width": 100},
    ]


def get_data(filters):
    conditions = "WHERE fo.docstatus = 1 AND fo.status = 'Delivered'"
    if filters.get("from_date"):
        conditions += " AND fo.scheduled_dispatch_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND fo.scheduled_dispatch_date <= %(to_date)s"
    if filters.get("customer"):
        conditions += " AND fo.customer = %(customer)s"
    if filters.get("route"):
        conditions += " AND fo.route = %(route)s"
    if filters.get("driver"):
        conditions += " AND fo.driver = %(driver)s"

    orders = frappe.db.sql(f"""
        SELECT
            fo.name, fo.customer, fo.route, fo.driver,
            fo.expected_delivery_date, fo.actual_delivery_date
        FROM `tabFreight Order` fo
        {conditions}
        ORDER BY fo.actual_delivery_date DESC
    """, filters, as_dict=True)

    result = []
    for o in orders:
        delay = 0
        status = "On Time"
        if o.expected_delivery_date and o.actual_delivery_date:
            exp = getdate(o.expected_delivery_date)
            act = getdate(o.actual_delivery_date)
            delay = (act - exp).days
            if delay > 0:
                status = f"Late ({delay}d)"
            elif delay < 0:
                status = f"Early ({abs(delay)}d)"

        result.append({
            "name": o.name,
            "customer": o.customer,
            "route": o.route,
            "driver": o.driver,
            "expected_delivery_date": o.expected_delivery_date,
            "actual_delivery_date": o.actual_delivery_date,
            "delay_days": delay,
            "delivery_status": status,
        })

    return result
