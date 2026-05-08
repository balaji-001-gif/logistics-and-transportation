import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today, flt


class FreightOrder(Document):

    def validate(self):
        self.validate_dates()
        self.fetch_driver_mobile()
        self.calculate_cargo_totals()
        self.calculate_charges_total()
        self.calculate_gst()

    def on_submit(self):
        self.db_set("status", "Dispatched")

    def on_cancel(self):
        self.db_set("status", "Cancelled")

    def validate_dates(self):
        if self.scheduled_dispatch_date and self.expected_delivery_date:
            if getdate(self.expected_delivery_date) < getdate(self.scheduled_dispatch_date):
                frappe.throw(_("Expected Delivery Date cannot be before Scheduled Dispatch Date."))
        if self.actual_delivery_date and self.scheduled_dispatch_date:
            if getdate(self.actual_delivery_date) < getdate(self.scheduled_dispatch_date):
                frappe.throw(_("Actual Delivery Date cannot be before Scheduled Dispatch Date."))

    def fetch_driver_mobile(self):
        if self.driver:
            mobile = frappe.db.get_value("Driver", self.driver, "mobile_number")
            self.driver_mobile = mobile or ""

    def calculate_cargo_totals(self):
        total_weight = 0.0
        total_volume = 0.0
        for row in (self.cargo_items or []):
            total_weight += flt(row.weight_kg)
            total_volume += flt(row.volume_cbm)
        self.total_weight_kg = total_weight
        self.total_volume_cbm = total_volume

    def calculate_charges_total(self):
        total_charges = sum(flt(row.amount) for row in (self.charges or []))
        self.total_charges = total_charges
        self.total_amount = flt(self.base_freight_amount) + total_charges

    def calculate_gst(self):
        taxable = flt(self.total_amount)
        if self.is_interstate:
            igst = taxable * (flt(self.igst_rate) / 100)
            self.igst_amount = igst
            self.cgst_amount = 0
            self.sgst_amount = 0
            self.total_gst_amount = igst
        else:
            cgst = taxable * (flt(self.cgst_rate) / 100)
            sgst = taxable * (flt(self.sgst_rate) / 100)
            self.cgst_amount = cgst
            self.sgst_amount = sgst
            self.igst_amount = 0
            self.total_gst_amount = cgst + sgst
        self.grand_total = taxable + flt(self.total_gst_amount)
