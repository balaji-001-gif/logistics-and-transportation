frappe.ui.form.on("Vendor Freight Bill", {
    base_freight_amount(frm) { frm.trigger("recalc"); },
    tds_rate(frm) { frm.trigger("recalc"); },
    amount_paid(frm) { frm.trigger("recalc"); },
    recalc(frm) {
        const base = frm.doc.base_freight_amount || 0;
        const tds = base * ((frm.doc.tds_rate || 2) / 100);
        const net = base - tds;
        frm.set_value("tds_amount", tds);
        frm.set_value("net_payable", net);
        frm.set_value("balance_due", net - (frm.doc.amount_paid || 0));
    },
    freight_order(frm) {
        if (frm.doc.freight_order) {
            frappe.db.get_doc("Freight Order", frm.doc.freight_order).then(fo => {
                frm.set_value("vehicle", fo.vehicle);
                frm.set_value("driver", fo.driver);
                frm.set_value("base_freight_amount", fo.base_freight_amount || 0);
            });
        }
    }
});
