frappe.ui.form.on("Outbound Shipment", {
    freight_order(frm) {
        if (frm.doc.freight_order) {
            frappe.db.get_doc("Freight Order", frm.doc.freight_order).then(fo => {
                frm.set_value("vehicle", fo.vehicle);
                frm.set_value("driver", fo.driver);
                frm.set_value("customer", fo.customer);
                frm.set_value("warehouse", fo.origin_warehouse);
            });
        }
    }
});

frappe.ui.form.on("Outbound Item", {
    ordered_qty(frm) { frm.trigger("recalc"); },
    picked_qty(frm) { frm.trigger("recalc"); },
    packed_qty(frm) { frm.trigger("recalc"); },
    items_remove(frm) { frm.trigger("recalc"); },
    recalc(frm) {
        let ord = 0, pick = 0, pack = 0;
        (frm.doc.items || []).forEach(r => {
            ord += r.ordered_qty || 0;
            pick += r.picked_qty || 0;
            pack += r.packed_qty || 0;
        });
        frm.set_value("total_ordered_qty", ord);
        frm.set_value("total_picked_qty", pick);
        frm.set_value("total_packed_qty", pack);
    }
});
