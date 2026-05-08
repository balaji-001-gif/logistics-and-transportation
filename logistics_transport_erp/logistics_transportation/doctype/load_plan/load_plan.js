frappe.ui.form.on("Load Plan", {
    vehicle(frm) {
        if (frm.doc.vehicle) {
            frappe.db.get_value("Vehicle", frm.doc.vehicle, ["payload_capacity_kg", "default_driver"], r => {
                frm.set_value("vehicle_capacity_kg", r.payload_capacity_kg || 0);
                if (!frm.doc.driver && r.default_driver) {
                    frm.set_value("driver", r.default_driver);
                }
                frm.trigger("recalc_load");
            });
        }
    },

    refresh(frm) {
        if (frm.doc.docstatus === 1 && frm.doc.status === "Confirmed") {
            frm.add_custom_button(__("Create Trip Sheet"), () => {
                frappe.new_doc("Trip Sheet", {
                    load_plan: frm.doc.name,
                    vehicle: frm.doc.vehicle,
                    driver: frm.doc.driver
                });
            }, __("Create"));
        }
    }
});

frappe.ui.form.on("Freight Order Row", {
    total_weight_kg(frm) { frm.trigger("recalc_load"); },
    freight_order_row_remove(frm) { frm.trigger("recalc_load"); },
    freight_order(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.freight_order) {
            frappe.db.get_doc("Freight Order", row.freight_order).then(fo => {
                frappe.model.set_value(cdt, cdn, "customer", fo.customer);
                frappe.model.set_value(cdt, cdn, "total_weight_kg", fo.total_weight_kg);
                frappe.model.set_value(cdt, cdn, "total_volume_cbm", fo.total_volume_cbm);
                frappe.model.set_value(cdt, cdn, "status", fo.status);
                frm.trigger("recalc_load");
            });
        }
    }
});

frappe.ui.form.on("Load Plan", {
    recalc_load(frm) {
        let w = 0, v = 0;
        (frm.doc.freight_orders || []).forEach(r => {
            w += r.total_weight_kg || 0;
            v += r.total_volume_cbm || 0;
        });
        frm.set_value("total_weight_kg", w);
        frm.set_value("total_volume_cbm", v);
        const cap = frm.doc.vehicle_capacity_kg || 0;
        frm.set_value("load_factor_percent", cap > 0 ? (w / cap) * 100 : 0);
    }
});
