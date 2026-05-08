frappe.ui.form.on("Warehouse", {
    gstin(frm) {
        if (frm.doc.gstin) {
            frm.set_value("gstin", frm.doc.gstin.toUpperCase().trim());
        }
    }
});
