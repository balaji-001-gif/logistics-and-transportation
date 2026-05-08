from frappe import _


def get_data():
    return [
        {
            "module_name": "Logistics Transportation",
            "app": "logistics_transport_erp",
            "label": _("Logistics Transportation"),
            "color": "#1a73e8",
            "icon": "uil uil-truck",
            "type": "module",
            "description": _("Freight, Fleet, Warehouse, Billing, and Compliance"),
        }
    ]
