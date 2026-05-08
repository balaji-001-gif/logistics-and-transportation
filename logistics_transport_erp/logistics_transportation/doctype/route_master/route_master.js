frappe.ui.form.on("Route Master", {
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
