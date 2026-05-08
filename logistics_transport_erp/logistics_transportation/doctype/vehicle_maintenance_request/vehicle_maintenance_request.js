frappe.ui.form.on("Vehicle Maintenance Request", {
    vehicle(frm) {
        if (frm.doc.vehicle) {
            frappe.db.get_value("Vehicle", frm.doc.vehicle,
                ["current_odometer_km", "default_driver"], r => {
                frm.set_value("odometer_at_request_km", r.current_odometer_km || 0);
                if (!frm.doc.raised_by_driver && r.default_driver) {
                    frm.set_value("raised_by_driver", r.default_driver);
                }
            });
        }
    },
    labour_cost(frm) { frm.trigger("recalc_cost"); },
    recalc_cost(frm) {
        let parts = 0;
        (frm.doc.parts_used || []).forEach(r => {
            parts += (r.quantity || 0) * (r.unit_cost || 0);
        });
        frm.set_value("total_parts_cost", parts);
        frm.set_value("total_maintenance_cost", parts + (frm.doc.labour_cost || 0));
    }
});

frappe.ui.form.on("Part Line", {
    quantity(frm, cdt, cdn) { recalc_part(frm, cdt, cdn); },
    unit_cost(frm, cdt, cdn) { recalc_part(frm, cdt, cdn); },
    parts_used_remove(frm) { frm.trigger("recalc_cost"); }
});

function recalc_part(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    frappe.model.set_value(cdt, cdn, "total_cost",
        (row.quantity || 0) * (row.unit_cost || 0)
    );
    frm.trigger("recalc_cost");
}
