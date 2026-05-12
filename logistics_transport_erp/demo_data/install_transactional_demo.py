"""
Freight Order + Trip Sheet + Tracking + EWB + POD + Complaint Demo Data
Called after install_demo_data.py (depends on vehicles, drivers, routes existing)
"""
import frappe
from frappe.utils import today, add_days, nowdate, now_datetime


def install_transactional_demo():
    frappe.set_user("Administrator")

    # ── Ensure demo customers exist in ERPNext ──────────────────────────────
    demo_customers = [
        {"customer_name": "Acme Electronics Pvt Ltd", "customer_group": "Commercial", "territory": "India"},
        {"customer_name": "Bharat Pharma Distributors", "customer_group": "Commercial", "territory": "India"},
        {"customer_name": "Sunrise FMCG Ltd", "customer_group": "Commercial", "territory": "India"},
        {"customer_name": "Chennai Auto Parts Co", "customer_group": "Commercial", "territory": "India"},
        {"customer_name": "Global Textile Exports", "customer_group": "Commercial", "territory": "India"},
    ]
    for c in demo_customers:
        if not frappe.db.exists("Customer", {"customer_name": c["customer_name"]}):
            cust = frappe.get_doc({"doctype": "Customer", **c})
            cust.insert(ignore_permissions=True)

    # ── Logistics Settings (Single) ─────────────────────────────────────────
    settings = frappe.get_single("Logistics Settings")
    settings.company_name = "BizAxl Logistics Solutions"
    settings.default_transport_mode = "Road FTL"
    settings.track_fuel_efficiency = 1
    settings.enable_predictive_maintenance = 1
    settings.save()

    # ── Customer Contracts ──────────────────────────────────────────────────
    contracts = [
        {"naming_series": "CCON-.YYYY.-.####", "contract_name": "Standard Logistics Agreement - Acme",
         "customer": _cust("Acme Electronics Pvt Ltd"), "contract_start_date": "2026-01-01",
         "contract_end_date": "2026-12-31", "is_active": 1, "service_level_agreement": "Standard (48-72h)"},
        {"naming_series": "CCON-.YYYY.-.####", "contract_name": "Pharma Express Contract - Bharat",
         "customer": _cust("Bharat Pharma Distributors"), "contract_start_date": "2026-02-15",
         "contract_end_date": "2027-02-14", "is_active": 1, "service_level_agreement": "Priority (24-36h)"},
    ]
    for c in contracts:
        if not frappe.db.exists("Customer Contract", {"contract_name": c["contract_name"]}):
            frappe.get_doc({"doctype": "Customer Contract", **c}).insert(ignore_permissions=True)

    # ── Freight Orders ──────────────────────────────────────────────────────
    freight_orders = [
        {
            "naming_series": "FO-.YYYY.-.#####",
            "status": "Delivered", "transport_mode": "Road FTL",
            "origin_warehouse": "Mumbai Hub", "destination_warehouse": "Delhi Gateway",
            "route": "Mumbai - Delhi",
            "customer": _cust("Acme Electronics Pvt Ltd"),
            "vehicle": "MH-12-AB-1234", "driver": _drv("Ramesh Kumar Singh"),
            "scheduled_dispatch_date": add_days(today(), -5),
            "expected_delivery_date": add_days(today(), -3),
            "actual_delivery_date": add_days(today(), -3),
            "base_freight_amount": 45000, "is_interstate": 1,
            "igst_rate": 18, "sac_code": "996511",
            "cargo_items": [
                {"description": "Electronic Components", "quantity": 50,
                 "unit": "PCS", "weight_kg": 1200, "volume_cbm": 4.5}
            ],
        },
        {
            "naming_series": "FO-.YYYY.-.#####",
            "status": "In Transit", "transport_mode": "Road FTL",
            "origin_warehouse": "Delhi Gateway", "destination_warehouse": "Bengaluru Cross-Dock",
            "route": "Delhi - Bengaluru",
            "customer": _cust("Bharat Pharma Distributors"),
            "vehicle": "DL-01-GH-5678", "driver": _drv("Suresh Prasad Yadav"),
            "scheduled_dispatch_date": add_days(today(), -2),
            "expected_delivery_date": add_days(today(), 1),
            "base_freight_amount": 68000, "is_interstate": 1,
            "igst_rate": 18, "sac_code": "996511",
            "cargo_items": [
                {"description": "Pharmaceutical Products", "quantity": 200,
                 "unit": "CARTON", "weight_kg": 3500, "volume_cbm": 12}
            ],
        },
        {
            "naming_series": "FO-.YYYY.-.#####",
            "status": "Dispatched", "transport_mode": "Road LTL",
            "origin_warehouse": "Mumbai Hub", "destination_warehouse": "Pune Spoke",
            "route": "Mumbai - Pune",
            "customer": _cust("Sunrise FMCG Ltd"),
            "vehicle": "MH-14-IJ-7890", "driver": _drv("Arun Gawde"),
            "scheduled_dispatch_date": today(),
            "expected_delivery_date": today(),
            "base_freight_amount": 4500, "is_interstate": 0,
            "cgst_rate": 9, "sgst_rate": 9, "sac_code": "996511",
            "cargo_items": [
                {"description": "FMCG Goods", "quantity": 30,
                 "unit": "CARTON", "weight_kg": 450, "volume_cbm": 2.1}
            ],
        },
        {
            "naming_series": "FO-.YYYY.-.#####",
            "status": "Booked", "transport_mode": "Road FTL",
            "origin_warehouse": "Chennai Port Facility", "destination_warehouse": "Hyderabad Spoke",
            "route": "Chennai - Hyderabad",
            "customer": _cust("Chennai Auto Parts Co"),
            "vehicle": "TN-22-EF-3456", "driver": _drv("Muthu Selvam"),
            "scheduled_dispatch_date": add_days(today(), 1),
            "expected_delivery_date": add_days(today(), 2),
            "base_freight_amount": 22000, "is_interstate": 1,
            "igst_rate": 18, "sac_code": "996511",
            "cargo_items": [
                {"description": "Automotive Parts", "quantity": 80,
                 "unit": "PCS", "weight_kg": 2800, "volume_cbm": 8}
            ],
        },
        {
            "naming_series": "FO-.YYYY.-.#####",
            "status": "Cancelled", "transport_mode": "Road FTL",
            "origin_warehouse": "Bengaluru Cross-Dock", "destination_warehouse": "Mumbai Hub",
            "route": "Bengaluru - Mumbai",
            "customer": _cust("Global Textile Exports"),
            "vehicle": "KA-09-CD-9012", "driver": _drv("Vijay Krishnamurthy"),
            "scheduled_dispatch_date": add_days(today(), -3),
            "expected_delivery_date": add_days(today(), -1),
            "base_freight_amount": 32000, "is_interstate": 1,
            "igst_rate": 18, "sac_code": "996511",
            "cargo_items": [
                {"description": "Textile Products", "quantity": 150,
                 "unit": "PALLET", "weight_kg": 5000, "volume_cbm": 18}
            ],
        },
        {
            "naming_series": "FO-.YYYY.-.#####",
            "status": "Delivered", "transport_mode": "Road FTL",
            "origin_warehouse": "Hyderabad Spoke", "destination_warehouse": "Mumbai Hub",
            "route": "Hyderabad - Pune",
            "customer": _cust("Acme Electronics Pvt Ltd"),
            "vehicle": "MH-12-AB-1234", "driver": _drv("Ramesh Kumar Singh"),
            "scheduled_dispatch_date": add_days(today(), -10),
            "expected_delivery_date": add_days(today(), -8),
            "actual_delivery_date": add_days(today(), -8),
            "base_freight_amount": 19500, "is_interstate": 1,
            "igst_rate": 18, "sac_code": "996511",
            "cargo_items": [
                {"description": "Chemical Drums", "quantity": 20,
                 "unit": "DRUM", "weight_kg": 4000, "volume_cbm": 10}
            ],
        },
    ]

    fo_names = []
    for fo_data in freight_orders:
        cargo = fo_data.pop("cargo_items")
        doc = frappe.get_doc({"doctype": "Freight Order", **fo_data})
        for c in cargo:
            doc.append("cargo_items", c)
        doc.insert(ignore_permissions=True)
        fo_names.append(doc.name)
    frappe.db.commit()

    # ── Consignment Notes (LR) ──────────────────────────────────────────────
    cns = [
        {"naming_series": "CN-.YYYY.-.#####", "lr_date": add_days(today(), -5),
         "freight_order": fo_names[0], "consignor_name": "Acme Electronics Pvt Ltd",
         "consignee_name": "Acme Delhi Branch Warehouse", "origin_city": "Mumbai", "destination_city": "New Delhi",
         "origin_address": "Plot 12, JNPT Road", "destination_address": "NH-44, Kundli"},
        {"naming_series": "CN-.YYYY.-.#####", "lr_date": add_days(today(), -2),
         "freight_order": fo_names[1], "consignor_name": "Bharat Pharma Distributors",
         "consignee_name": "MedPlus Bengaluru", "origin_city": "New Delhi", "destination_city": "Bengaluru",
         "origin_address": "NH-44, Kundli", "destination_address": "Hoskote Industrial Area"},
    ]
    for cn in cns:
        doc = frappe.get_doc({"doctype": "Consignment Note", **cn})
        doc.append("goods_items", {"description": "Electronics", "quantity": 50, "unit": "PCS", "weight_kg": 1200})
        doc.insert(ignore_permissions=True)
    frappe.db.commit()

    # ── Trip Sheets ─────────────────────────────────────────────────────────
    trip_sheets = [
        {"naming_series": "TS-.YYYY.-.#####", "trip_date": add_days(today(), -5),
         "vehicle": "MH-12-AB-1234", "driver": _drv("Ramesh Kumar Singh"),
         "start_odometer_km": 48000, "end_odometer_km": 49420, "status": "Completed",
         "origin": "Mumbai Hub", "destination": "Delhi Gateway"},
        {"naming_series": "TS-.YYYY.-.#####", "trip_date": add_days(today(), -2),
         "vehicle": "DL-01-GH-5678", "driver": _drv("Suresh Prasad Yadav"),
         "start_odometer_km": 81200, "status": "In Transit",
         "origin": "Delhi Gateway", "destination": "Bengaluru Cross-Dock"},
    ]
    ts_names = []
    for ts in trip_sheets:
        doc = frappe.get_doc({"doctype": "Trip Sheet", **ts})
        doc.append("fuel_entries", {"fuel_station": "Reliance Petrol Pump", "quantity_litres": 120, "rate_per_litre": 95, "amount": 11400})
        doc.append("toll_entries", {"toll_plaza_name": "Khed-Shivapur Toll", "amount": 120})
        doc.insert(ignore_permissions=True)
        ts_names.append(doc.name)
    frappe.db.commit()

    # ── PODs ────────────────────────────────────────────────────────────────
    pods = [
        {"naming_series": "POD-.YYYY.-.#####", "freight_order": fo_names[0],
         "delivery_datetime": f"{add_days(today(), -3)} 16:45:00", "receiver_name": "Sanjay Sharma",
         "status": "Delivered", "remarks": "Delivered in good condition."},
        {"naming_series": "POD-.YYYY.-.#####", "freight_order": fo_names[5],
         "delivery_datetime": f"{add_days(today(), -8)} 11:30:00", "receiver_name": "Rahul Mehta",
         "status": "Delivered", "remarks": "Minor scratches on drum surface, but seals intact."},
    ]
    for p in pods:
        frappe.get_doc({"doctype": "POD", **p}).insert(ignore_permissions=True)
    frappe.db.commit()

    # ── Freight Invoices ────────────────────────────────────────────────────
    invoices = [
        {"naming_series": "FINV-.YYYY.-.#####", "invoice_date": add_days(today(), -2),
         "customer": _cust("Acme Electronics Pvt Ltd"), "total_amount": 45000,
         "tax_amount": 8100, "grand_total": 53100, "status": "Draft"},
    ]
    for inv in invoices:
        doc = frappe.get_doc({"doctype": "Freight Invoice", **inv})
        doc.append("lr_references", {"freight_order": fo_names[0], "amount": 45000})
        doc.append("gst_details", {
            "sac_code": "996511", "taxable_amount": 45000,
            "igst_rate": 18, "igst_amount": 8100, "total_gst": 8100
        })
        doc.insert(ignore_permissions=True)

    # ── Freight Settlements ─────────────────────────────────────────────────
    settlements = [
        {"naming_series": "FS-.YYYY.-.#####", "settlement_date": today(),
         "trip_sheet": ts_names[0], "driver": _drv("Ramesh Kumar Singh"),
         "total_advance_paid": 8000, "total_expenses": 7200, "balance_amount": 800,
         "status": "Submitted"},
    ]
    for fs in settlements:
        frappe.get_doc({"doctype": "Freight Settlement", **fs}).insert(ignore_permissions=True)

    # ── Load Plans ──────────────────────────────────────────────────────────
    load_plans = [
        {"naming_series": "LP-.YYYY.-.#####", "planned_date": add_days(today(), 1),
         "vehicle": "MH-12-AB-1234", "warehouse": "Mumbai Hub", "status": "Draft"},
    ]
    for lp in load_plans:
        doc = frappe.get_doc({"doctype": "Load Plan", **lp})
        doc.append("freight_orders", {"freight_order": fo_names[3], "weight_kg": 2800, "volume_cbm": 8})
        doc.insert(ignore_permissions=True)

    # ── Stock Transfer Orders ───────────────────────────────────────────────
    stos = [
        {"naming_series": "STO-.YYYY.-.#####", "transfer_date": today(),
         "from_warehouse": "Mumbai Hub", "to_warehouse": "Pune Spoke", "status": "Draft"},
    ]
    for sto in stos:
        doc = frappe.get_doc({"doctype": "Stock Transfer Order", **sto})
        doc.append("items", {"item_description": "Safety Vests & Helmets", "quantity": 100, "uom": "PCS"})
        doc.insert(ignore_permissions=True)

    # ── Shipments (Inbound/Outbound) ────────────────────────────────────────
    outs = [
        {"naming_series": "OUT-.YYYY.-.#####", "dispatch_date": add_days(today(), -5),
         "warehouse": "Mumbai Hub", "freight_order": fo_names[0], "status": "Dispatched"},
    ]
    for o in outs:
        frappe.get_doc({"doctype": "Outbound Shipment", **o}).insert(ignore_permissions=True)

    inbs = [
        {"naming_series": "INB-.YYYY.-.#####", "receipt_date": add_days(today(), -3),
         "warehouse": "Delhi Gateway", "freight_order": fo_names[0], "status": "Received"},
    ]
    for i in inbs:
        frappe.get_doc({"doctype": "Inbound Shipment", **i}).insert(ignore_permissions=True)

    # ── Toll and Detention Charges ──────────────────────────────────────────
    tolls = [
        {"naming_series": "TDC-.YYYY.-.#####", "charge_type": "Toll", "charge_date": add_days(today(), -4),
         "vehicle": "MH-12-AB-1234", "amount": 1200, "location": "Nashik Expressway"},
        {"naming_series": "TDC-.YYYY.-.#####", "charge_type": "Detention", "charge_date": add_days(today(), -3),
         "vehicle": "MH-12-AB-1234", "amount": 2500, "location": "Delhi Gateway", "remarks": "Delayed by customer for unloading"},
    ]
    for t in tolls:
        frappe.get_doc({"doctype": "Toll and Detention Charge", **t}).insert(ignore_permissions=True)

    # ── Vendor Freight Bills ────────────────────────────────────────────────
    vfbs = [
        {"naming_series": "VFB-.YYYY.-.#####", "bill_date": add_days(today(), -1),
         "transporter_name": "Blue Dart Express", "base_freight_amount": 15000, "tax_amount": 2700,
         "total_bill_amount": 17700, "status": "Pending Approval"},
    ]
    for vfb in vfbs:
        frappe.get_doc({"doctype": "Vendor Freight Bill", **vfb}).insert(ignore_permissions=True)

    # ── Shipment Tracking Events (already done, but adding one for the IT order)
    # (Existing block handles this)

    # ── E-Way Bills (already done)
    # (Existing block handles this)

    # ── Customer Complaints (already done)
    # (Existing block handles this)

    # ── Fuel Logs (already done)
    # (Existing block handles this)

    # ── Advance Payment Requests (already done)
    # (Existing block handles this)

    # ── Dock Appointments (already done)
    # (Existing block handles this)

    frappe.db.commit()
    print("✅ Full Transactional demo data installed successfully!")
    print(f"   Freight Orders:      {len(fo_names)}")
    print(f"   Consignment Notes:   {len(cns)}")
    print(f"   Trip Sheets:         {len(trip_sheets)}")
    print(f"   PODs:                {len(pods)}")
    print(f"   Freight Invoices:    {len(invoices)}")
    print(f"   Freight Settlements: {len(settlements)}")
    print(f"   Load Plans:          {len(load_plans)}")
    print(f"   Stock Transfers:     {len(stos)}")
    print(f"   Shipments (IN/OUT):  2")
    print(f"   Toll/Detention:      {len(tolls)}")
    print(f"   Vendor Bills:        {len(vfbs)}")


def _drv(full_name):
    return frappe.db.get_value("Driver", {"full_name": full_name}, "name") or full_name


def _cust(customer_name):
    return frappe.db.get_value("Customer", {"customer_name": customer_name}, "name") or customer_name
