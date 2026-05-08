frappe.ui.form.on("Toll and Detention Charge", {
    freight_order(frm) {
        if (frm.doc.freight_order) {
            frappe.db.get_value("Freight Order", frm.doc.freight_order, "customer", r => {
                frm.set_value("customer", r.customer);
            });
        }
    }
});
