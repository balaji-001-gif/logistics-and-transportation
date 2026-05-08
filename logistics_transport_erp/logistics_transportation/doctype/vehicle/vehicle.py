import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


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
