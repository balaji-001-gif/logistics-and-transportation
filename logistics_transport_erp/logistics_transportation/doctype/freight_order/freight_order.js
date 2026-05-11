frappe.ui.form.on("Freight Order", {
    refresh(frm) {
        if (!frm.is_new() && frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Create Consignment Note"), () => {
                frappe.new_doc("Consignment Note", {
                    freight_order: frm.doc.name,
                    customer: frm.doc.customer,
                    vehicle: frm.doc.vehicle,
                    driver: frm.doc.driver
                });
            }, __("Create"));

            frm.add_custom_button(__("Create E-Way Bill"), () => {
                frappe.new_doc("E Way Bill", {
                    freight_order: frm.doc.name,
                    vehicle: frm.doc.vehicle
                });
            }, __("Create"));
        }

        // Status indicator
        const colors = {
            "Booked": "blue", "Dispatched": "orange",
            "In Transit": "yellow", "At Destination": "purple",
            "Delivered": "green", "Cancelled": "red"
        };
        if (frm.doc.status) {
            frm.page.set_indicator(frm.doc.status, colors[frm.doc.status] || "gray");
        }

        // Render route map if route is set
        if (!frm.is_new() && frm.doc.route) {
            frappe.db.get_doc("Route Master", frm.doc.route).then(route => {
                if (route.lat_origin && route.lat_destination) {
                    const origin = `${route.lat_origin},${route.lng_origin}`;
                    const destination = `${route.lat_destination},${route.lng_destination}`;
                    
                    // Fetch tracking events for pins
                    frappe.call({
                        method: "frappe.client.get_list",
                        args: {
                            doctype: "Shipment Tracking Event",
                            filters: { freight_order: frm.doc.name },
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
    },

    driver(frm) {
        if (frm.doc.driver) {
            frappe.db.get_value("Driver", frm.doc.driver, "mobile_number", (r) => {
                frm.set_value("driver_mobile", r.mobile_number || "");
            });
        }
    },

    base_freight_amount(frm) { frm.trigger("calculate_totals"); },
    is_interstate(frm) { frm.trigger("calculate_totals"); },
    cgst_rate(frm) { frm.trigger("calculate_totals"); },
    sgst_rate(frm) { frm.trigger("calculate_totals"); },
    igst_rate(frm) { frm.trigger("calculate_totals"); },

    calculate_totals(frm) {
        let charges = 0;
        (frm.doc.charges || []).forEach(r => charges += (r.amount || 0));
        const total = (frm.doc.base_freight_amount || 0) + charges;
        frm.set_value("total_charges", charges);
        frm.set_value("total_amount", total);

        let gst = 0;
        if (frm.doc.is_interstate) {
            const igst = total * ((frm.doc.igst_rate || 18) / 100);
            frm.set_value("igst_amount", igst);
            frm.set_value("cgst_amount", 0);
            frm.set_value("sgst_amount", 0);
            gst = igst;
        } else {
            const cgst = total * ((frm.doc.cgst_rate || 9) / 100);
            const sgst = total * ((frm.doc.sgst_rate || 9) / 100);
            frm.set_value("cgst_amount", cgst);
            frm.set_value("sgst_amount", sgst);
            frm.set_value("igst_amount", 0);
            gst = cgst + sgst;
        }
        frm.set_value("total_gst_amount", gst);
        frm.set_value("grand_total", total + gst);
    }
});

frappe.ui.form.on("Cargo Item", {
    weight_kg(frm) { frm.trigger("recalc_cargo"); },
    volume_cbm(frm) { frm.trigger("recalc_cargo"); },
    cargo_items_remove(frm) { frm.trigger("recalc_cargo"); },
    recalc_cargo(frm) {
        let w = 0, v = 0;
        (frm.doc.cargo_items || []).forEach(r => {
            w += r.weight_kg || 0;
            v += r.volume_cbm || 0;
        });
        frm.set_value("total_weight_kg", w);
        frm.set_value("total_volume_cbm", v);
    }
});

frappe.ui.form.on("Freight Charge", {
    amount(frm) { frm.trigger("calculate_totals"); },
    freight_charge_remove(frm) { frm.trigger("calculate_totals"); }
});
