import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today, now_datetime


class Vehicle(Document):

    def validate(self):
        self.check_document_expiry()

    def check_document_expiry(self):
        for doc in (self.documents or []):
            if doc.expiry_date and getdate(doc.expiry_date) < getdate(today()):
                frappe.msgprint(
                    _("{0} ({1}) has expired on {2}").format(
                        doc.document_type, doc.document_number or "", doc.expiry_date
                    ),
                    alert=True,
                    indicator="red"
                )

    def verify_rc(self):
        """Called via the 'Verify RC' button — queries Vahan API and saves result."""
        from logistics_transport_erp.api.vahan_api import check_rc_status
        result = check_rc_status(self.registration_number)
        self.db_set("rc_status",      result.get("rc_status", "Unknown"), notify=True)
        self.db_set("rc_fitness_upto", result.get("fitness_upto") or None, notify=True)
        self.db_set("rc_owner_name",   result.get("owner_name", ""),       notify=True)
        self.db_set("rc_verified_on",  now_datetime(),                     notify=True)
        return result


@frappe.whitelist()
def verify_vehicle_rc(vehicle_name):
    """Whitelisted endpoint for the 'Verify RC' button."""
    doc = frappe.get_doc("Vehicle", vehicle_name)
    result = doc.verify_rc()
    indicator = "green" if result.get("rc_status") == "Active" else "red"
    frappe.msgprint(result.get("message", "Verification complete."), alert=True, indicator=indicator)
    return result
