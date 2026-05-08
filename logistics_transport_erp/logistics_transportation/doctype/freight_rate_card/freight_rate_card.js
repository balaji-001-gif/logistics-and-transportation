frappe.ui.form.on("Freight Rate Card", {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__("Duplicate Rate Card"), () => {
                frappe.model.copy_doc(frm.doc);
            });
        }
    }
});
