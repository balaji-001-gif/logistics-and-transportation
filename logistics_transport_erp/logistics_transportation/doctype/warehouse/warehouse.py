import frappe
from frappe import _
from frappe.model.document import Document


class Warehouse(Document):

    def validate(self):
        if self.gstin:
            self.gstin = self.gstin.strip().upper()
            if len(self.gstin) != 15:
                frappe.throw(_("GSTIN must be exactly 15 characters."))
