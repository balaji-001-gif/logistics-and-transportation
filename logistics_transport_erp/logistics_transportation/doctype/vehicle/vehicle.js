frappe.ui.form.on("Vehicle", {
    refresh(frm) {
        if (!frm.is_new()) {
            // Highlight expired documents
            (frm.doc.documents || []).forEach(row => {
                if (row.expiry_date) {
                    const expiry = frappe.datetime.str_to_obj(row.expiry_date);
                    const today = frappe.datetime.str_to_obj(frappe.datetime.get_today());
                    if (expiry < today) {
                        frappe.show_alert({
                            message: __(`${row.document_type} EXPIRED`),
                            indicator: "red"
                        });
                    }
                }
            });
        }
    }
});
