frappe.ui.form.on("Fuel Log", {
    vehicle(frm) {
        if (frm.doc.vehicle) {
            frappe.db.get_value("Vehicle", frm.doc.vehicle,
                ["current_odometer_km", "default_driver", "fuel_type"], r => {
                frm.set_value("previous_odometer_km", r.current_odometer_km || 0);
                if (!frm.doc.driver && r.default_driver) {
                    frm.set_value("driver", r.default_driver);
                }
                if (r.fuel_type) frm.set_value("fuel_type", r.fuel_type);
            });
        }
    },
    quantity_litres(frm) { frm.trigger("recalc"); },
    rate_per_litre(frm) { frm.trigger("recalc"); },
    odometer_reading_km(frm) { frm.trigger("recalc"); },
    recalc(frm) {
        frm.set_value("total_amount",
            (frm.doc.quantity_litres || 0) * (frm.doc.rate_per_litre || 0)
        );
        const dist = (frm.doc.odometer_reading_km || 0) - (frm.doc.previous_odometer_km || 0);
        frm.set_value("distance_since_last_fill", dist > 0 ? dist : 0);
        const litres = frm.doc.quantity_litres || 0;
        frm.set_value("fuel_efficiency_kmpl", litres > 0 && dist > 0 ? dist / litres : 0);
    }
});
