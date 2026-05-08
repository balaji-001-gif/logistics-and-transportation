frappe.ui.form.on("Shipment Tracking Event", {
    refresh(frm) {
        const colors = {
            "Booked": "blue", "Dispatched": "orange", "In Transit": "yellow",
            "At Hub": "cyan", "Out for Delivery": "purple", "Delivered": "green",
            "Delay": "red", "Exception": "red", "Returned": "gray"
        };
        if (frm.doc.event_type) {
            frm.page.set_indicator(frm.doc.event_type, colors[frm.doc.event_type] || "gray");
        }
    },
    freight_order(frm) {
        if (frm.doc.freight_order) {
            frappe.db.get_doc("Freight Order", frm.doc.freight_order).then(fo => {
                if (fo.driver) frm.set_value("updated_by_driver", fo.driver);
            });
        }
    }
});
