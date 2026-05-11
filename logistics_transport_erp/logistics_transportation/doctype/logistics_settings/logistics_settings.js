frappe.ui.form.on("Logistics Settings", {
    refresh(frm) {
        frm.set_intro(
            __("Configure API credentials and alert thresholds for the Logistics & Transportation ERP."),
            "blue"
        );
    }
});
