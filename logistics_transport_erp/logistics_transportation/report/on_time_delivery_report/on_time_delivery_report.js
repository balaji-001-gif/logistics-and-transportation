frappe.query_reports["On-Time Delivery Report"] = {
    filters: [
        {fieldname: "from_date", label: __("From Date"), fieldtype: "Date",
         default: frappe.datetime.add_months(frappe.datetime.get_today(), -1)},
        {fieldname: "to_date", label: __("To Date"), fieldtype: "Date",
         default: frappe.datetime.get_today()},
        {fieldname: "customer", label: __("Customer"), fieldtype: "Link", options: "Customer"},
        {fieldname: "route", label: __("Route"), fieldtype: "Link", options: "Route Master"},
        {fieldname: "driver", label: __("Driver"), fieldtype: "Link", options: "Driver"},
    ]
};
