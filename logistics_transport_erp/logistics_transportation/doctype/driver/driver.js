frappe.ui.form.on("Driver", {
    refresh(frm) {
        if (!frm.is_new() && frm.doc.dl_expiry_date) {
            const expiry = frappe.datetime.str_to_obj(frm.doc.dl_expiry_date);
            const today = frappe.datetime.str_to_obj(frappe.datetime.get_today());
            const daysLeft = Math.floor((expiry - today) / (1000 * 60 * 60 * 24));
            if (daysLeft < 0) {
                frm.set_intro(__("⚠️ Driving Licence EXPIRED"), "red");
            } else if (daysLeft <= 30) {
                frm.set_intro(__(`⚠️ Driving Licence expires in ${daysLeft} days`), "orange");
            }
        }
    }
});
