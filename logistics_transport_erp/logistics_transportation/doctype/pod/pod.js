frappe.ui.form.on("POD", {
    freight_order(frm) {
        if (frm.doc.freight_order) {
            frappe.db.get_doc("Freight Order", frm.doc.freight_order).then(fo => {
                frm.set_value("driver", fo.driver);
            });
        }
    },
    refresh(frm) {
        const colors = {
            "Pending": "orange", "Delivered": "green",
            "Partial": "yellow", "Exception": "red", "Returned": "gray"
        };
        if (frm.doc.status) {
            frm.page.set_indicator(frm.doc.status, colors[frm.doc.status] || "gray");
        }
        if (!frm.is_new() && frm.doc.status === "Delivered") {
            frm.set_intro(__("✅ Proof of Delivery confirmed"), "green");
        }
    }
});
