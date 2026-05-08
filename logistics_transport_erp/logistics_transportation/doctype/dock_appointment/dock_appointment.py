import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime


class DockAppointment(Document):

    def validate(self):
        self.validate_times()

    def validate_times(self):
        if self.scheduled_start_time and self.scheduled_end_time:
            if self.scheduled_end_time <= self.scheduled_start_time:
                frappe.throw(_("Scheduled End Time must be after Start Time."))

    def on_submit(self):
        self.db_set("status", "Completed")
