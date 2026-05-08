frappe.ui.form.on("Dock Appointment", {
    refresh(frm) {
        const colors = {
            "Scheduled": "blue", "In Progress": "orange",
            "Completed": "green", "Cancelled": "red", "No Show": "gray"
        };
        if (frm.doc.status) {
            frm.page.set_indicator(frm.doc.status, colors[frm.doc.status] || "gray");
        }
    },
    freight_order(frm) {
        if (frm.doc.freight_order) {
            frappe.db.get_doc("Freight Order", frm.doc.freight_order).then(fo => {
                frm.set_value("vehicle", fo.vehicle);
                frm.set_value("driver", fo.driver);
            });
        }
    }
});
