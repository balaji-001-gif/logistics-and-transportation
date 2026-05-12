import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
        {"label": _("Month"), "fieldname": "month", "fieldtype": "Data", "width": 100},
        {"label": _("Output GST (INR)"), "fieldname": "output_gst", "fieldtype": "Currency", "width": 150},
        {"label": _("Input GST / ITC (INR)"), "fieldname": "input_gst", "fieldtype": "Currency", "width": 170},
        {"label": _("Net GST Liability (INR)"), "fieldname": "net_liability", "fieldtype": "Currency", "width": 170},
        {"label": _("CGST Output"), "fieldname": "cgst_output", "fieldtype": "Currency", "width": 130},
        {"label": _("SGST Output"), "fieldname": "sgst_output", "fieldtype": "Currency", "width": 130},
        {"label": _("IGST Output"), "fieldname": "igst_output", "fieldtype": "Currency", "width": 130},
    ]


def get_data(filters):
    conditions = "WHERE fi.docstatus = 1"
    if filters.get("from_date"):
        conditions += " AND fi.invoice_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND fi.invoice_date <= %(to_date)s"

    output = frappe.db.sql(f"""
        SELECT
            DATE_FORMAT(fi.invoice_date, '%%Y-%%m') as month,
            SUM(fi.total_gst_amount) as output_gst,
            SUM(fi.cgst_amount) as cgst_output,
            SUM(fi.sgst_amount) as sgst_output,
            SUM(fi.igst_amount) as igst_output
        FROM `tabFreight Invoice` fi
        {conditions}
        GROUP BY DATE_FORMAT(fi.invoice_date, '%%Y-%%m')
        ORDER BY month DESC
    """, filters, as_dict=True)

    input_gst = frappe.db.sql(f"""
        SELECT
            DATE_FORMAT(vfb.bill_date, '%%Y-%%m') as month,
            SUM(vfb.igst_amount) as input_gst
        FROM `tabVendor Freight Bill` vfb
        WHERE vfb.docstatus = 1 AND vfb.is_rcm = 1
        {'AND vfb.bill_date >= %(from_date)s' if filters.get('from_date') else ''}
        {'AND vfb.bill_date <= %(to_date)s' if filters.get('to_date') else ''}
        GROUP BY DATE_FORMAT(vfb.bill_date, '%%Y-%%m')
    """, filters, as_dict=True)

    input_by_month = {r.month: flt(r.input_gst) for r in input_gst}

    result = []
    for row in output:
        ig = input_by_month.get(row.month, 0)
        result.append({
            "month": row.month,
            "output_gst": flt(row.output_gst),
            "input_gst": ig,
            "net_liability": flt(row.output_gst) - ig,
            "cgst_output": flt(row.cgst_output),
            "sgst_output": flt(row.sgst_output),
            "igst_output": flt(row.igst_output),
        })

    return result
