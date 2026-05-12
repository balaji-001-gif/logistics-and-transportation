"""
Clear Demo Data for Logistics & Transportation ERP
Run via: bench --site [site] execute logistics_transport_erp.demo_data.clear_demo_data.run
"""
import frappe


def run():
    frappe.set_user("Administrator")
    print("🗑️ Clearing Logistics ERP Demo Data...")

    # Order matters due to links (Transactions first)
    doctypes = [
        "Shipment Tracking Event",
        "POD",
        "E Way Bill",
        "Customer Complaint",
        "Fuel Log",
        "Advance Payment Request",
        "Dock Appointment",
        "Freight Invoice",
        "Freight Settlement",
        "Consignment Note",
        "Toll and Detention Charge",
        "Outbound Shipment",
        "Inbound Shipment",
        "Stock Transfer Order",
        "Load Plan",
        "Freight Order",
        "Trip Sheet",
        "Vehicle Maintenance Request",
        "Freight Rate Card",
        "Route Master",
        "Vehicle",
        "Driver",
        "Warehouse",
        "Vehicle Type",
        "Customer Contract"
    ]

    for dt in doctypes:
        try:
            # Delete all records of this doctype for a clean demo state
            # (Assuming this is a demo site as per user request)
            frappe.db.sql(f"DELETE FROM `tab{dt}`")
            frappe.db.commit()
            print(f"   Cleared: {dt}")
        except Exception as e:
            print(f"   ⚠️ Could not clear {dt}: {str(e)}")

    # Clear specific demo customers from ERPNext
    demo_customers = [
        "Acme Electronics Pvt Ltd",
        "Bharat Pharma Distributors",
        "Sunrise FMCG Ltd",
        "Chennai Auto Parts Co",
        "Global Textile Exports"
    ]
    for cust in demo_customers:
        # Delete by customer_name since primary ID might be a series
        names = frappe.get_all("Customer", filters={"customer_name": cust}, pluck="name")
        for n in names:
            try:
                frappe.delete_doc("Customer", n, ignore_permissions=True, force=True)
                print(f"   Deleted Customer: {cust}")
            except Exception:
                pass

    frappe.db.commit()
    print("✨ Demo data cleared successfully!")
