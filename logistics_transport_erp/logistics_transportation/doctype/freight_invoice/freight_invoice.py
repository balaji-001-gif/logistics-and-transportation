import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, today, add_days


class FreightInvoice(Document):

    def validate(self):
        self.calculate_totals()
        self.set_due_date()
        self.check_overdue()

    def on_submit(self):
        self.db_set("status", "Submitted")

    def on_cancel(self):
        self.db_set("status", "Cancelled")

    def calculate_totals(self):
        subtotal = sum(flt(row.freight_amount) for row in (self.lr_references or []))
        self.subtotal = subtotal

        total_gst = 0.0
        for row in (self.gst_details or []):
            taxable = flt(row.taxable_amount)
            cgst = taxable * (flt(row.cgst_rate) / 100)
            sgst = taxable * (flt(row.sgst_rate) / 100)
            igst = taxable * (flt(row.igst_rate) / 100)
            row.cgst_amount = cgst
            row.sgst_amount = sgst
            row.igst_amount = igst
            row.total_gst = cgst + sgst + igst
            total_gst += row.total_gst

        self.total_gst_amount = total_gst
        self.grand_total = subtotal + total_gst
        self.balance_due = self.grand_total - flt(self.amount_paid)

    def set_due_date(self):
        if self.invoice_date and self.payment_terms and not self.due_date:
            days_map = {
                "7 Days Net": 7, "15 Days Net": 15,
                "30 Days Net": 30, "45 Days Net": 45,
                "Advance": 0, "COD": 0
            }
            days = days_map.get(self.payment_terms, 30)
            self.due_date = add_days(self.invoice_date, days)

    def check_overdue(self):
        if self.due_date and self.status == "Submitted":
            if getdate(self.due_date) < getdate(today()):
                self.status = "Overdue"
