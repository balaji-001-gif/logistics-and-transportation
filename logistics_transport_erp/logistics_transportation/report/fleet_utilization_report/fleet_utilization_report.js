frappe.query_reports["Fleet Utilization Report"] = {
    filters: [
        {fieldname: "from_date", label: __("From Date"), fieldtype: "Date",
         default: frappe.datetime.add_months(frappe.datetime.get_today(), -1)},
        {fieldname: "to_date", label: __("To Date"), fieldtype: "Date",
         default: frappe.datetime.get_today()},
        {fieldname: "vehicle_type", label: __("Vehicle Type"), fieldtype: "Link", options: "Vehicle Type"},
    ]
};
