import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class CustomerContract(Document):

    def validate(self):
        if self.contract_start_date and self.contract_end_date:
            if getdate(self.contract_end_date) < getdate(self.contract_start_date):
                frappe.throw(_("Contract End Date cannot be before Start Date."))

        self.check_expiry()

    def check_expiry(self):
        if self.contract_end_date and getdate(self.contract_end_date) < getdate(today()):
            if self.status == "Active":
                self.status = "Expired"
                frappe.msgprint(_("Contract has been automatically marked as Expired."), alert=True)
