import frappe
from frappe import _
from frappe.utils import flt, date_diff, today, getdate


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
        {"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 150},
        {"label": _("Item Description"), "fieldname": "item_description", "fieldtype": "Data", "width": 200},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Data", "width": 150},
        {"label": _("Receipt Date"), "fieldname": "receipt_date", "fieldtype": "Date", "width": 120},
        {"label": _("Qty Received"), "fieldname": "qty_received", "fieldtype": "Float", "width": 110},
        {"label": _("Dwell Days"), "fieldname": "dwell_days", "fieldtype": "Int", "width": 100},
        {"label": _("Ageing Bucket"), "fieldname": "ageing_bucket", "fieldtype": "Data", "width": 120},
    ]


def get_data(filters):
    conditions = "WHERE ins.docstatus = 1"
    if filters.get("warehouse"):
        conditions += " AND ins.warehouse = %(warehouse)s"
    if filters.get("from_date"):
        conditions += " AND ins.receipt_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND ins.receipt_date <= %(to_date)s"

    items = frappe.db.sql(f"""
        SELECT
            ins.warehouse,
            ini.item_description,
            fo.customer,
            ins.receipt_date,
            ini.received_qty as qty_received
        FROM `tabInbound Shipment` ins
        JOIN `tabInbound Item` ini ON ini.parent = ins.name
        LEFT JOIN `tabFreight Order` fo ON fo.name = ins.freight_order
        {conditions}
        ORDER BY ins.receipt_date ASC
    """, filters, as_dict=True)

    result = []
    today_date = getdate(today())

    for item in items:
        dwell = date_diff(today_date, getdate(item.receipt_date)) if item.receipt_date else 0
        if dwell <= 7:
            bucket = "0-7 Days"
        elif dwell <= 30:
            bucket = "8-30 Days"
        elif dwell <= 60:
            bucket = "31-60 Days"
        else:
            bucket = "60+ Days"

        result.append({
            "warehouse": item.warehouse,
            "item_description": item.item_description,
            "customer": item.customer or "",
            "receipt_date": item.receipt_date,
            "qty_received": flt(item.qty_received),
            "dwell_days": dwell,
            "ageing_bucket": bucket,
        })

    return result
