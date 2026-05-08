frappe.ui.form.on("Advance Payment Request", {
    amount_disbursed(frm) { frm.trigger("recalc"); },
    amount_recovered(frm) { frm.trigger("recalc"); },
    recalc(frm) {
        frm.set_value("balance_outstanding",
            (frm.doc.amount_disbursed || 0) - (frm.doc.amount_recovered || 0)
        );
    },
    driver(frm) {
        if (frm.doc.driver) {
            frappe.db.get_value("Driver", frm.doc.driver, "full_name", r => {
                if (!frm.doc.payee_name) frm.set_value("payee_name", r.full_name);
            });
        }
    }
});
