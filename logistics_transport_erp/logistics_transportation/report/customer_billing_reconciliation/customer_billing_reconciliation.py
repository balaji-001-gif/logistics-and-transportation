import frappe
from frappe import _
from frappe.utils import flt, getdate, today


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 160},
        {"label": _("Unbilled Shipments"), "fieldname": "unbilled_count", "fieldtype": "Int", "width": 150},
        {"label": _("Unbilled Amount (INR)"), "fieldname": "unbilled_amount", "fieldtype": "Currency", "width": 170},
        {"label": _("Total Invoiced (INR)"), "fieldname": "invoiced_amount", "fieldtype": "Currency", "width": 160},
        {"label": _("Total Paid (INR)"), "fieldname": "paid_amount", "fieldtype": "Currency", "width": 140},
        {"label": _("Balance Due (INR)"), "fieldname": "balance_due", "fieldtype": "Currency", "width": 140},
        {"label": _("Overdue Invoices"), "fieldname": "overdue_count", "fieldtype": "Int", "width": 140},
    ]


def get_data(filters):
    customers = frappe.get_all("Customer", fields=["name"])
    result = []

    for c in customers:
        unbilled = frappe.db.sql("""
            SELECT COUNT(*) as cnt, SUM(grand_total) as amt
            FROM `tabFreight Order`
            WHERE customer = %s AND docstatus = 1
              AND status = 'Delivered'
              AND name NOT IN (
                  SELECT IFNULL(freight_order, '') FROM `tabFI LR Row`
              )
        """, c.name, as_dict=True)[0]

        invoiced = frappe.db.sql("""
            SELECT SUM(grand_total) as total, SUM(amount_paid) as paid,
                   SUM(balance_due) as balance,
                   SUM(CASE WHEN status = 'Overdue' THEN 1 ELSE 0 END) as overdue
            FROM `tabFreight Invoice`
            WHERE customer = %s AND docstatus = 1
        """, c.name, as_dict=True)[0]

        total_inv = flt(invoiced.total)
        if total_inv == 0 and flt(unbilled.cnt) == 0:
            continue

        result.append({
            "customer": c.name,
            "unbilled_count": int(unbilled.cnt or 0),
            "unbilled_amount": flt(unbilled.amt),
            "invoiced_amount": total_inv,
            "paid_amount": flt(invoiced.paid),
            "balance_due": flt(invoiced.balance),
            "overdue_count": int(invoiced.overdue or 0),
        })

    return sorted(result, key=lambda x: x["balance_due"], reverse=True)
