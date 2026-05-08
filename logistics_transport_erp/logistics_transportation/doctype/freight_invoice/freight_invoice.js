frappe.ui.form.on("Freight Invoice", {
    amount_paid(frm) {
        const balance = (frm.doc.grand_total || 0) - (frm.doc.amount_paid || 0);
        frm.set_value("balance_due", balance);
        if (balance <= 0 && frm.doc.docstatus === 1) {
            frm.set_value("status", "Paid");
        } else if (frm.doc.amount_paid > 0 && balance > 0) {
            frm.set_value("status", "Partially Paid");
        }
    },
    customer_contract(frm) {
        if (frm.doc.customer_contract) {
            frappe.db.get_value("Customer Contract", frm.doc.customer_contract,
                ["payment_terms", "sac_code"], r => {
                if (r.payment_terms) frm.set_value("payment_terms", r.payment_terms);
            });
        }
    }
});

frappe.ui.form.on("Freight Invoice LR Row", {
    freight_order(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.freight_order) {
            frappe.db.get_doc("Freight Order", row.freight_order).then(fo => {
                frappe.model.set_value(cdt, cdn, "freight_amount", fo.grand_total || 0);
                frappe.model.set_value(cdt, cdn, "origin",
                    fo.origin_warehouse || fo.origin_address || "");
                frappe.model.set_value(cdt, cdn, "destination",
                    fo.destination_warehouse || fo.destination_address || "");
            });
        }
    },
    freight_amount(frm) { frm.trigger("recalc"); },
    lr_references_remove(frm) { frm.trigger("recalc"); },
    recalc(frm) {
        const sub = (frm.doc.lr_references || [])
            .reduce((s, r) => s + (r.freight_amount || 0), 0);
        frm.set_value("subtotal", sub);
    }
});

frappe.ui.form.on("Freight Invoice GST Row", {
    taxable_amount(frm, cdt, cdn) { recalc_gst(frm, cdt, cdn); },
    cgst_rate(frm, cdt, cdn) { recalc_gst(frm, cdt, cdn); },
    sgst_rate(frm, cdt, cdn) { recalc_gst(frm, cdt, cdn); },
    igst_rate(frm, cdt, cdn) { recalc_gst(frm, cdt, cdn); },
    gst_details_remove(frm) { frm.trigger("recalc_gst_total"); }
});

function recalc_gst(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    const taxable = row.taxable_amount || 0;
    const cgst = taxable * ((row.cgst_rate || 0) / 100);
    const sgst = taxable * ((row.sgst_rate || 0) / 100);
    const igst = taxable * ((row.igst_rate || 0) / 100);
    frappe.model.set_value(cdt, cdn, "cgst_amount", cgst);
    frappe.model.set_value(cdt, cdn, "sgst_amount", sgst);
    frappe.model.set_value(cdt, cdn, "igst_amount", igst);
    frappe.model.set_value(cdt, cdn, "total_gst", cgst + sgst + igst);
    frm.trigger("recalc_gst_total");
}

frappe.ui.form.on("Freight Invoice", {
    recalc_gst_total(frm) {
        const total_gst = (frm.doc.gst_details || [])
            .reduce((s, r) => s + (r.total_gst || 0), 0);
        frm.set_value("total_gst_amount", total_gst);
        frm.set_value("grand_total", (frm.doc.subtotal || 0) + total_gst);
        frm.set_value("balance_due", (frm.doc.grand_total || 0) - (frm.doc.amount_paid || 0));
    }
});
