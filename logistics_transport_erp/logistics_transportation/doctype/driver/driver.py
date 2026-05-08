import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


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
