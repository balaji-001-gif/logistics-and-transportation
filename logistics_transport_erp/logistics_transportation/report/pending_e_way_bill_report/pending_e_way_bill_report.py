import frappe
from frappe import _
from frappe.utils import now_datetime


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
        {"label": _("Freight Order"), "fieldname": "freight_order", "fieldtype": "Link", "options": "Freight Order", "width": 150},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Link", "options": "Vehicle", "width": 130},
        {"label": _("Dispatch Date"), "fieldname": "dispatch_date", "fieldtype": "Date", "width": 120},
        {"label": _("E-Way Bill No"), "fieldname": "ewb_number", "fieldtype": "Data", "width": 140},
        {"label": _("Valid Upto"), "fieldname": "valid_upto", "fieldtype": "Datetime", "width": 150},
        {"label": _("EWB Status"), "fieldname": "ewb_status", "fieldtype": "Data", "width": 110},
        {"label": _("Issue"), "fieldname": "issue", "fieldtype": "Data", "width": 150},
    ]


def get_data(filters):
    in_transit = frappe.db.sql("""
        SELECT fo.name as freight_order, fo.customer, fo.vehicle,
               fo.scheduled_dispatch_date as dispatch_date
        FROM `tabFreight Order` fo
        WHERE fo.docstatus = 1
          AND fo.status IN ('Dispatched', 'In Transit', 'At Destination')
        ORDER BY fo.scheduled_dispatch_date
    """, as_dict=True)

    result = []
    now = str(now_datetime())

    for fo in in_transit:
        ewb = frappe.db.get_value(
            "E Way Bill",
            {"freight_order": fo.freight_order, "status": ["not in", ["Cancelled"]]},
            ["ewb_number", "valid_upto", "status"],
            as_dict=True
        )

        if not ewb:
            result.append({**fo, "ewb_number": None, "valid_upto": None,
                          "ewb_status": "Missing", "issue": "No E-Way Bill generated"})
        elif ewb.valid_upto and str(ewb.valid_upto) < now:
            result.append({**fo, "ewb_number": ewb.ewb_number,
                          "valid_upto": ewb.valid_upto, "ewb_status": "Expired",
                          "issue": "E-Way Bill expired"})
        elif ewb.status == "Expired":
            result.append({**fo, "ewb_number": ewb.ewb_number,
                          "valid_upto": ewb.valid_upto, "ewb_status": "Expired",
                          "issue": "Needs extension"})

    return result
