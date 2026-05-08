frappe.ui.form.on("Customer Contract", {
    refresh(frm) {
        if (frm.doc.contract_end_date) {
            const expiry = frappe.datetime.str_to_obj(frm.doc.contract_end_date);
            const today = frappe.datetime.str_to_obj(frappe.datetime.get_today());
            const daysLeft = Math.floor((expiry - today) / (1000 * 60 * 60 * 24));
            if (daysLeft < 0) {
                frm.set_intro(__("⚠️ This contract has EXPIRED"), "red");
            } else if (daysLeft <= 30) {
                frm.set_intro(__(`⚠️ This contract expires in ${daysLeft} days`), "orange");
            }
        }
    }
});
