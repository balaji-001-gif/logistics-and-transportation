frappe.ui.form.on("Stock Transfer Order", {
    gst_applicable(frm) { frm.trigger("recalc"); },
    recalc(frm) {
        let qty = 0, val = 0;
        (frm.doc.items || []).forEach(r => {
            qty += r.quantity || 0;
            val += (r.quantity || 0) * (r.unit_value || 0);
        });
        frm.set_value("total_quantity", qty);
        frm.set_value("total_value", val);
        if (frm.doc.gst_applicable) {
            const cgst = val * 0.09;
            const sgst = val * 0.09;
            frm.set_value("cgst_amount", cgst);
            frm.set_value("sgst_amount", sgst);
            frm.set_value("igst_amount", 0);
            frm.set_value("grand_total", val + cgst + sgst);
        } else {
            frm.set_value("cgst_amount", 0);
            frm.set_value("sgst_amount", 0);
            frm.set_value("igst_amount", 0);
            frm.set_value("grand_total", val);
        }
    }
});

frappe.ui.form.on("Stock Transfer Item", {
    quantity(frm) { frm.trigger("recalc"); },
    unit_value(frm) { frm.trigger("recalc"); },
    items_remove(frm) { frm.trigger("recalc"); }
});
