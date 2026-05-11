frappe.ui.form.on("Trip Sheet", {
    refresh(frm) {
        // Render route map if load plan is set
        if (!frm.is_new() && frm.doc.load_plan) {
            frappe.db.get_value("Load Plan", frm.doc.load_plan, "freight_orders", lp => {
                const orders = lp.freight_orders || [];
                if (orders.length > 0) {
                    // For now, use the first order's route
                    frappe.db.get_value("Freight Order", orders[0].freight_order, "route", fo => {
                        if (fo.route) {
                            frappe.db.get_doc("Route Master", fo.route).then(route => {
                                if (route.lat_origin && route.lat_destination) {
                                    const origin = `${route.lat_origin},${route.lng_origin}`;
                                    const destination = `${route.lat_destination},${route.lng_destination}`;
                                    
                                    // Fetch tracking events for pins across all orders in the trip
                                    const order_names = orders.map(o => o.freight_order);
                                    frappe.call({
                                        method: "frappe.client.get_list",
                                        args: {
                                            doctype: "Shipment Tracking Event",
                                            filters: { freight_order: ["in", order_names] },
                                            fields: ["latitude", "longitude", "event_type", "location_description"]
                                        },
                                        callback(r) {
                                            const pins = (r.message || []).map(p => ({
                                                lat: p.latitude,
                                                lng: p.longitude,
                                                event_type: p.event_type,
                                                label: p.location_description
                                            }));
                                            if (window.LogisticsRouteMap) {
                                                window.LogisticsRouteMap.render(frm, { origin, destination, trackingPins: pins });
                                            }
                                        }
                                    });
                                }
                            });
                        }
                    });
                }
            });
        }
    },

    load_plan(frm) {
        if (frm.doc.load_plan) {
            frappe.db.get_doc("Load Plan", frm.doc.load_plan).then(lp => {
                frm.set_value("vehicle", lp.vehicle);
                frm.set_value("driver", lp.driver);
            });
        }
    },

    vehicle(frm) {
        if (frm.doc.vehicle) {
            frappe.db.get_value("Vehicle", frm.doc.vehicle, "current_odometer_km", r => {
                if (!frm.doc.start_odometer_km) {
                    frm.set_value("start_odometer_km", r.current_odometer_km || 0);
                }
            });
        }
    },

    end_odometer_km(frm) { frm.trigger("recalc"); },
    start_odometer_km(frm) { frm.trigger("recalc"); },
    driver_advance_given(frm) { frm.trigger("recalc_balance"); },
    driver_advance_recovered(frm) { frm.trigger("recalc_balance"); },

    recalc(frm) {
        const dist = (frm.doc.end_odometer_km || 0) - (frm.doc.start_odometer_km || 0);
        frm.set_value("distance_covered_km", dist > 0 ? dist : 0);
        frm.trigger("recalc_balance");
    },

    recalc_balance(frm) {
        const toll = (frm.doc.total_toll_amount || 0);
        const fuel = (frm.doc.total_fuel_amount || 0);
        const given = (frm.doc.driver_advance_given || 0);
        const recovered = (frm.doc.driver_advance_recovered || 0);
        frm.set_value("driver_balance", given - toll - fuel - recovered);
    }
});

frappe.ui.form.on("Toll Entry", {
    amount(frm) { frm.trigger("recalc_tolls"); },
    toll_entries_remove(frm) { frm.trigger("recalc_tolls"); },
    recalc_tolls(frm) {
        const total = (frm.doc.toll_entries || []).reduce((s, r) => s + (r.amount || 0), 0);
        frm.set_value("total_toll_amount", total);
        frm.trigger("recalc_balance");
    }
});

frappe.ui.form.on("Trip Fuel Entry", {
    quantity_litres(frm) { frm.trigger("recalc_fuel"); },
    rate_per_litre(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "amount",
            (row.quantity_litres || 0) * (row.rate_per_litre || 0)
        );
        frm.trigger("recalc_fuel");
    },
    amount(frm) { frm.trigger("recalc_fuel"); },
    fuel_entries_remove(frm) { frm.trigger("recalc_fuel"); },
    recalc_fuel(frm) {
        let litres = 0, amount = 0;
        (frm.doc.fuel_entries || []).forEach(r => {
            litres += r.quantity_litres || 0;
            amount += r.amount || 0;
        });
        frm.set_value("total_fuel_litres", litres);
        frm.set_value("total_fuel_amount", amount);
        const dist = frm.doc.distance_covered_km || 0;
        frm.set_value("fuel_efficiency_kmpl", litres > 0 ? dist / litres : 0);
        frm.trigger("recalc_balance");
    }
});
