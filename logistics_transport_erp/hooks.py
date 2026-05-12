app_name = "logistics_transport_erp"
app_title = "Logistics & Transportation ERP"
app_publisher = "Your Company"
app_description = "Full-stack logistics & transportation ERP for India"
app_email = "dev@yourcompany.com"
app_license = "MIT"
app_version = "0.0.1"

required_apps = ["frappe", "erpnext"]

app_include_css = "/assets/logistics_transport_erp/css/logistics_transport_erp.css"
app_include_js = [
    "/assets/logistics_transport_erp/js/logistics_transport_erp.js",
    "/assets/logistics_transport_erp/js/route_map.js",
]

doc_events = {}

scheduler_events = {
    "daily": [
        "logistics_transport_erp.tasks.auto_maintenance_check",
        "logistics_transport_erp.tasks.check_ewb_expiry",
    ],
    "weekly": [],
}

fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "Logistics Transportation"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "Logistics Transportation"]]},
    "Vehicle Type",
    "Logistics Settings",
    {"dt": "Notification", "filters": [["document_type", "in", [
        "Vehicle Document", "E Way Bill", "Freight Order",
        "Freight Invoice", "Vehicle", "Driver",
        "Vehicle Maintenance Request",
    ]]]},
    {"dt": "Report", "filters": [["module", "=", "Logistics Transportation"]]},
    {"dt": "Workspace", "filters": [["module", "=", "Logistics Transportation"]]},
]

website_route_rules = [
    {"from_route": "/driver-portal", "to_route": "driver_portal"},
]

before_migrate = "logistics_transport_erp.install.before_migrate"
after_install = "logistics_transport_erp.install.after_install"

override_doctype_class = {
    "FI LR Row": "logistics_transport_erp.logistics_transportation.doctype.fi_lr_row.fi_lr_row.FreightInvoiceLrRow",
    "FI GST Row": "logistics_transport_erp.logistics_transportation.doctype.fi_gst_row.fi_gst_row.FreightInvoiceGstRow",
    "Toll and Detention Charge": "logistics_transport_erp.logistics_transportation.doctype.toll_and_detention_charge.toll_and_detention_charge.TollAndDetentionCharge",
    "Shipment Tracking Event": "logistics_transport_erp.logistics_transportation.doctype.shipment_tracking_event.shipment_tracking_event.ShipmentTrackingEvent",
    "POD": "logistics_transport_erp.logistics_transportation.doctype.pod.pod.Pod",
    "Customer Complaint": "logistics_transport_erp.logistics_transportation.doctype.customer_complaint.customer_complaint.CustomerComplaint",
}
