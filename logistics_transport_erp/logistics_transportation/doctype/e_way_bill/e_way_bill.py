import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class EWayBill(Document):

    def validate(self):
        self.validate_validity()
        self.check_expiry_status()

    def validate_validity(self):
        if self.generated_date and self.valid_upto:
            if self.valid_upto <= self.generated_date:
                frappe.throw(_("Valid Upto must be after Generated Date."))

    def check_expiry_status(self):
        if self.valid_upto and self.status not in ("Cancelled", "Delivered"):
            if self.valid_upto < str(now_datetime()):
                self.status = "Expired"
                frappe.msgprint(
                    _("E-Way Bill {0} has expired.").format(self.ewb_number or self.name),
                    alert=True, indicator="red"
                )
