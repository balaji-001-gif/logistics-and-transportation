import json
import os

import frappe


def execute():
    ws_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "workspace", "logistics_transport_erp", "logistics_transport_erp.json"
    )
    if not os.path.exists(ws_path):
        return

    with open(ws_path) as f:
        ws_data = json.load(f)

    if frappe.db.exists("Workspace", "Logistics & Transportation"):
        doc = frappe.get_doc("Workspace", "Logistics & Transportation")
        doc.update({
            "title": ws_data.get("title"),
            "icon": ws_data.get("icon"),
            "category": ws_data.get("category", "Modules"),
            "public": 1,
            "is_hidden": 0,
            "content": ws_data.get("content", "[]"),
            "shortcuts": ws_data.get("shortcuts", []),
        })
        doc.save(ignore_permissions=True)
    else:
        for field in ("creation", "modified", "modified_by", "owner"):
            ws_data.pop(field, None)
        doc = frappe.get_doc(ws_data)
        doc.insert(ignore_permissions=True)

    frappe.db.commit()
