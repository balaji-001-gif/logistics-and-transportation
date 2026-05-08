frappe.ui.form.on("Consignment Note", {
    freight_order(frm) {
        if (frm.doc.freight_order) {
            frappe.db.get_doc("Freight Order", frm.doc.freight_order).then(fo => {
                frm.set_value("vehicle", fo.vehicle);
                frm.set_value("driver", fo.driver);
                frm.set_value("freight_amount", fo.grand_total);
            });
        }
    },
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Create E-Way Bill"), () => {
                frappe.new_doc("E Way Bill", {
                    consignment_note: frm.doc.name,
                    freight_order: frm.doc.freight_order,
                    vehicle: frm.doc.vehicle
                });
            }, __("Create"));
        }
    }
});

frappe.ui.form.on("Goods Item", {
    packages(frm) { frm.trigger("recalc"); },
    weight_kg(frm) { frm.trigger("recalc"); },
    goods_items_remove(frm) { frm.trigger("recalc"); },
    recalc(frm) {
        let pkgs = 0, wt = 0;
        (frm.doc.goods_items || []).forEach(r => {
            pkgs += r.packages || 0;
            wt += r.weight_kg || 0;
        });
        frm.set_value("total_packages", pkgs);
        frm.set_value("total_weight_kg", wt);
    }
});
