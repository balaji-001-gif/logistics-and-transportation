frappe.ui.form.on("Route Master", {
    refresh(frm) {
        if (!frm.is_new()) {
            // ── Fetch Coordinates & Distance button ───────────────────────
            frm.add_custom_button(__("Fetch Coordinates & Distance (Maps)"), function () {
                frappe.show_alert({ message: __("Geocoding via Google Maps…"), indicator: "blue" });
                frappe.call({
                    method: "logistics_transport_erp.logistics_transportation.doctype.route_master.route_master.fetch_route_coordinates",
                    args:   { route_name: frm.doc.name },
                    callback(r) {
                        if (r.message) {
                            frm.reload_doc();
                        }
                    }
                });
            }, __("Actions"));

            // ── Render route map if coordinates are available ──────────────
            if (frm.doc.lat_origin && frm.doc.lat_destination) {
                const origin      = `${frm.doc.lat_origin},${frm.doc.lng_origin}`;
                const destination = `${frm.doc.lat_destination},${frm.doc.lng_destination}`;
                if (window.LogisticsRouteMap) {
                    window.LogisticsRouteMap.render(frm, { origin, destination });
                }
            }
        }
    },
    origin_city(frm) {
        frm.trigger("suggest_route_name");
    },
    destination_city(frm) {
        frm.trigger("suggest_route_name");
    },
    suggest_route_name(frm) {
        if (frm.is_new() && frm.doc.origin_city && frm.doc.destination_city) {
            frm.set_value("route_name", `${frm.doc.origin_city} - ${frm.doc.destination_city}`);
        }
    }
});
