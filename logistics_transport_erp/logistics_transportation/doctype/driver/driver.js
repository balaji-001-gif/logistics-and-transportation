frappe.ui.form.on("Driver", {
    refresh(frm) {
        if (!frm.is_new()) {
            // DL expiry banner
            if (frm.doc.dl_expiry_date) {
                const expiry   = frappe.datetime.str_to_obj(frm.doc.dl_expiry_date);
                const today    = frappe.datetime.str_to_obj(frappe.datetime.get_today());
                const daysLeft = Math.floor((expiry - today) / (1000 * 60 * 60 * 24));
                if (daysLeft < 0) {
                    frm.set_intro(__("⚠️ Driving Licence EXPIRED"), "red");
                } else if (daysLeft <= 30) {
                    frm.set_intro(__(`⚠️ Driving Licence expires in ${daysLeft} days`), "orange");
                }
            }

            // ── Verify DL button ──────────────────────────────────────────
            frm.add_custom_button(__("Verify DL (Sarathi)"), function () {
                frappe.show_alert({ message: __("Contacting Sarathi API…"), indicator: "blue" });
                frappe.call({
                    method: "logistics_transport_erp.logistics_transportation.doctype.driver.driver.verify_driver_dl",
                    args:   { driver_name: frm.doc.name },
                    callback(r) {
                        if (r.message) {
                            frm.reload_doc();
                        }
                    }
                });
            }, __("Actions"));

            // ── Colour DL verified status ─────────────────────────────────
            if (frm.doc.dl_verified_status) {
                const colour = frm.doc.dl_verified_status === "Active" ? "green" : "red";
                frm.get_field("dl_verified_status").$input_wrapper
                    .find(".control-value")
                    .css("color", colour)
                    .css("font-weight", "bold");
            }
        }
    }
});

