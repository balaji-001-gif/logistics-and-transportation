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

    def generate_ewb_via_api(self):
        """Calls NIC API to generate E-Way Bill and saves the result."""
        from logistics_transport_erp.api.ewb_api import generate_ewb
        result = generate_ewb(self)
        self.db_set("ewb_number",     result["ewb_number"],  notify=True)
        self.db_set("valid_upto",     result["valid_upto"],  notify=True)
        self.db_set("generated_date", result["ewb_date"],    notify=True)
        self.db_set("status",         "Generated",           notify=True)
        return result


@frappe.whitelist()
def generate_e_way_bill(ewb_name):
    """Whitelisted endpoint for the 'Generate E-Way Bill' button."""
    doc = frappe.get_doc("E Way Bill", ewb_name)
    if doc.status == "Generated":
        frappe.throw(_("E-Way Bill {0} has already been generated (EWB No: {1}).").format(
            doc.name, doc.ewb_number
        ))
    result = doc.generate_ewb_via_api()
    frappe.msgprint(
        _("✅ E-Way Bill Generated Successfully!\nEWB Number: {0}\nValid Upto: {1}").format(
            result["ewb_number"], result["valid_upto"]
        ),
        title="EWB Generated",
        indicator="green"
    )
    return result
