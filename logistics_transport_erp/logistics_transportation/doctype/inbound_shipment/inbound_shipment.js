frappe.ui.form.on("Inbound Shipment", {
    freight_order(frm) {
        if (frm.doc.freight_order) {
            frappe.db.get_doc("Freight Order", frm.doc.freight_order).then(fo => {
                frm.set_value("vehicle", fo.vehicle);
                frm.set_value("driver", fo.driver);
                frm.set_value("warehouse", fo.destination_warehouse);
            });
        }
    },
    refresh(frm) {
        const colors = {
            "Draft": "gray", "Received": "blue",
            "Putaway": "green", "Cancelled": "red"
        };
        if (frm.doc.status) {
            frm.page.set_indicator(frm.doc.status, colors[frm.doc.status] || "gray");
        }
    }
});

frappe.ui.form.on("Inbound Item", {
    received_qty(frm) { frm.trigger("recalc"); },
    expected_qty(frm) { frm.trigger("recalc"); },
    is_damaged(frm) { frm.trigger("recalc"); },
    items_remove(frm) { frm.trigger("recalc"); },
    recalc(frm) {
        let exp = 0, rec = 0, dmg = 0;
        (frm.doc.items || []).forEach(r => {
            exp += flt(r.expected_qty);
            rec += flt(r.received_qty);
            if (r.is_damaged) dmg++;
        });
        frm.set_value("total_expected_qty", exp);
        frm.set_value("total_received_qty", rec);
        frm.set_value("shortage_qty", Math.max(0, exp - rec));
        frm.set_value("damage_count", dmg);
    }
});
