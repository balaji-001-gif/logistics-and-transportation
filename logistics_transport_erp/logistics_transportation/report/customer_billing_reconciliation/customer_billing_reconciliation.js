frappe.query_reports["Customer Billing Reconciliation"] = {
    filters: [
        {fieldname: "customer", label: __("Customer"), fieldtype: "Link", options: "Customer"},
    ]
};
