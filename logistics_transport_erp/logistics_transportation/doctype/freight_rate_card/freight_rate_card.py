import frappe
from frappe import _
from frappe.model.document import Document


class FreightRateCard(Document):

    def validate(self):
        if self.effective_from and self.effective_to:
            if self.effective_to < self.effective_from:
                frappe.throw(_("Effective To date cannot be before Effective From date."))
