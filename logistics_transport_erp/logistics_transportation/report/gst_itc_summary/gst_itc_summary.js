frappe.query_reports["GST ITC Summary"] = {
    filters: [
        {fieldname: "from_date", label: __("From Date"), fieldtype: "Date",
         default: frappe.datetime.add_months(frappe.datetime.get_today(), -3)},
        {fieldname: "to_date", label: __("To Date"), fieldtype: "Date",
         default: frappe.datetime.get_today()},
    ]
};
