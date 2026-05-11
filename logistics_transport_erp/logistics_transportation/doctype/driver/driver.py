import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today, now_datetime


class Driver(Document):

    def validate(self):
        self.validate_dl_expiry()

    def validate_dl_expiry(self):
        if self.dl_expiry_date:
            if getdate(self.dl_expiry_date) < getdate(today()):
                frappe.msgprint(
                    _("Warning: Driving Licence for {0} has expired on {1}").format(
                        self.full_name, self.dl_expiry_date
                    ),
                    alert=True,
                    indicator="red"
                )

    def verify_dl(self):
        """Called via the 'Verify DL (Sarathi)' button."""
        from logistics_transport_erp.api.vahan_api import check_dl_status
        dob = str(self.date_of_birth) if self.date_of_birth else ""
        result = check_dl_status(self.primary_dl_number or "", dob)
        self.db_set("dl_verified_status", result.get("dl_status", "Unknown"), notify=True)
        self.db_set("dl_valid_upto",      result.get("valid_upto") or None,   notify=True)
        self.db_set("dl_verified_class",  result.get("dl_class", ""),         notify=True)
        self.db_set("dl_verified_on",     now_datetime(),                     notify=True)
        return result


@frappe.whitelist()
def verify_driver_dl(driver_name):
    """Whitelisted endpoint for the 'Verify DL' button."""
    doc = frappe.get_doc("Driver", driver_name)
    result = doc.verify_dl()
    indicator = "green" if result.get("dl_status") == "Active" else "red"
    frappe.msgprint(result.get("message", "Verification complete."), alert=True, indicator=indicator)
    return result
