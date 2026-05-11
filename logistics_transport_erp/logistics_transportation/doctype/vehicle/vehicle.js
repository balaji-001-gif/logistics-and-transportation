frappe.ui.form.on("Vehicle", {
    refresh(frm) {
        if (!frm.is_new()) {
            // Highlight expired documents
            (frm.doc.documents || []).forEach(row => {
                if (row.expiry_date) {
                    const expiry = frappe.datetime.str_to_obj(row.expiry_date);
                    const today  = frappe.datetime.str_to_obj(frappe.datetime.get_today());
                    if (expiry < today) {
                        frappe.show_alert({
                            message: __(`${row.document_type} EXPIRED`),
                            indicator: "red"
                        });
                    }
                }
            });

            // ── Verify RC button ──────────────────────────────────────────
            frm.add_custom_button(__("Verify RC (Vahan)"), function () {
                frappe.show_alert({ message: __("Contacting Vahan API…"), indicator: "blue" });
                frappe.call({
                    method: "logistics_transport_erp.logistics_transportation.doctype.vehicle.vehicle.verify_vehicle_rc",
                    args:   { vehicle_name: frm.doc.name },
                    callback(r) {
                        if (r.message) {
                            frm.reload_doc();
                        }
                    }
                });
            }, __("Actions"));

            // ── Colour RC status ──────────────────────────────────────────
            if (frm.doc.rc_status) {
                const colour = frm.doc.rc_status === "Active" ? "green" : "red";
                frm.get_field("rc_status").$input_wrapper
                    .find(".control-value")
                    .css("color", colour)
                    .css("font-weight", "bold");
            }
        }
    }
});

