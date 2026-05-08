frappe.ui.form.on("Customer Complaint", {
    freight_order(frm) {
        if (frm.doc.freight_order) {
            frappe.db.get_value("Freight Order", frm.doc.freight_order, "customer", r => {
                frm.set_value("customer", r.customer);
            });
        }
    },
    refresh(frm) {
        const colors = {
            "Open": "red", "Under Review": "orange",
            "Resolved": "green", "Closed": "gray", "Escalated": "purple"
        };
        if (frm.doc.resolution_status) {
            frm.page.set_indicator(
                frm.doc.resolution_status,
                colors[frm.doc.resolution_status] || "gray"
            );
        }
    }
});
