frappe.ui.form.on("E Way Bill", {
    refresh(frm) {
        if (frm.doc.valid_upto) {
            const expiry = new Date(frm.doc.valid_upto);
            const now = new Date();
            const hoursLeft = Math.floor((expiry - now) / (1000 * 60 * 60));
            if (hoursLeft < 0) {
                frm.set_intro(__("⚠️ E-Way Bill EXPIRED"), "red");
            } else if (hoursLeft <= 6) {
                frm.set_intro(__(`⚠️ E-Way Bill expires in ${hoursLeft} hours`), "orange");
            } else if (hoursLeft <= 24) {
                frm.set_intro(__(`⚠️ E-Way Bill expires in ${hoursLeft} hours`), "yellow");
            }
        }
    },

    freight_order(frm) {
        if (frm.doc.freight_order) {
            frappe.db.get_doc("Freight Order", frm.doc.freight_order).then(fo => {
                frm.set_value("vehicle", fo.vehicle);
                frm.set_value("taxable_value", fo.total_amount);
                frm.set_value("cgst_amount", fo.cgst_amount);
                frm.set_value("sgst_amount", fo.sgst_amount);
                frm.set_value("igst_amount", fo.igst_amount);
                frm.set_value("total_invoice_value", fo.grand_total);
            });
        }
    }
});
