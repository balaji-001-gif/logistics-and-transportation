"""
Master entry point for all demo data installation.
Usage:
    bench --site [site] execute logistics_transport_erp.logistics_transportation.demo_data.setup_all.run_all
"""
import frappe


def run_all():
    from logistics_transport_erp.logistics_transportation.demo_data.install_demo_data import install_demo_data
    from logistics_transport_erp.logistics_transportation.demo_data.install_transactional_demo import install_transactional_demo

    print("🚀 Installing Logistics ERP Demo Data...")
    install_demo_data()
    install_transactional_demo()
    print("\n✅ All demo data installed successfully!")
    print("\nNaming Series Summary:")
    print("  Drivers              → DRV-.YYYY.-.####")
    print("  Freight Orders       → FO-.YYYY.-.#####")
    print("  Trip Sheets          → TS-.YYYY.-.#####")
    print("  E-Way Bills          → EWB-.YYYY.-.#####")
    print("  Vehicle Maint. Req.  → VMR-.YYYY.-.#####")
    print("  Consignment Notes    → CN-.YYYY.-.#####")
    print("  Freight Invoice      → FINV-.YYYY.-.#####")
    print("  Freight Settlement   → FS-.YYYY.-.#####")
    print("  Customer Contract    → CCON-.YYYY.-.####")
    print("  Customer Complaint   → CC-.YYYY.-.#####")
    print("  Freight Rate Card    → FRC-.YYYY.-.####")
    print("  Load Plan            → LP-.YYYY.-.#####")
    print("  POD                  → POD-.YYYY.-.#####")
    print("  Tracking Event       → STE-.YYYY.-.#####")
    print("  Fuel Log             → FL-.YYYY.-.#####")
    print("  Advance Payment Req. → APR-.YYYY.-.#####")
    print("  Dock Appointment     → DA-.YYYY.-.#####")
    print("  Vendor Freight Bill  → VFB-.YYYY.-.#####")
    print("  Inbound Shipment     → INB-.YYYY.-.#####")
    print("  Outbound Shipment    → OUT-.YYYY.-.#####")
    print("  Stock Transfer Order → STO-.YYYY.-.#####")
    print("  Toll & Detention     → TDC-.YYYY.-.#####")
