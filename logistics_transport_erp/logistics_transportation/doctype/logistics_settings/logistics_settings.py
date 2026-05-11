import frappe
from frappe.model.document import Document


class LogisticsSettings(Document):
    pass


def get_settings():
    """Utility: returns the Logistics Settings singleton."""
    return frappe.get_single("Logistics Settings")
