import json
import os

import frappe


def before_migrate():
    _ensure_child_doctype("FI LR Row", "Logistics Transportation")
    _ensure_child_doctype("FI GST Row", "Logistics Transportation")
    _ensure_child_doctype("Toll and Detention Charge", "Logistics Transportation")


def _ensure_child_doctype(name, module):
    if not frappe.db.exists("DocType", name):
        frappe.db.sql("""
            INSERT IGNORE INTO `tabDocType`
            (name, module, istable, engine, creation, modified,
             modified_by, owner, docstatus, `_liked_by`)
            VALUES (%s, %s, 1, 'InnoDB', NOW(), NOW(),
                    'Administrator', 'Administrator', 0, '[]')
        """, (name, module))
        frappe.db.commit()


def after_install():
    create_workspace()
    frappe.db.commit()


def create_workspace():
    if frappe.db.exists("Workspace", "Logistics Transportation"):
        return
    ws_path = os.path.join(
        os.path.dirname(__file__),
        "workspace", "logistics_transport_erp", "logistics_transport_erp.json"
    )
    if not os.path.exists(ws_path):
        frappe.log_error(f"Workspace JSON not found at {ws_path}", "Install")
        return
    with open(ws_path) as f:
        ws_data = json.load(f)
    for field in ("creation", "modified", "modified_by", "owner"):
        ws_data.pop(field, None)
    doc = frappe.get_doc(ws_data)
    doc.insert(ignore_permissions=True)
