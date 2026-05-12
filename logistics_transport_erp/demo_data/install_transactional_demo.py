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
                 "uom": "Nos", "weight_kg": 1200, "volume_cbm": 4.5}
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
                 "uom": "Boxes", "weight_kg": 3500, "volume_cbm": 12}
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
                 "uom": "Cartons", "weight_kg": 450, "volume_cbm": 2.1}
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
                 "uom": "Nos", "weight_kg": 2800, "volume_cbm": 8}
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
                 "uom": "Bundles", "weight_kg": 5000, "volume_cbm": 18}
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
                 "uom": "Drums", "weight_kg": 4000, "volume_cbm": 10}
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

    # ── Shipment Tracking Events ────────────────────────────────────────────
    fo_del = fo_names[0]   # Delivered order
    fo_it  = fo_names[1]   # In Transit order
    tracking_events = [
        {"freight_order": fo_del, "event_type": "Dispatched",
         "event_datetime": f"{add_days(today(),-5)} 08:30:00",
         "location_description": "Mumbai Hub", "city": "Mumbai", "state": "Maharashtra",
         "latitude": "19.0760", "longitude": "72.8777"},
        {"freight_order": fo_del, "event_type": "At Hub",
         "event_datetime": f"{add_days(today(),-4)} 14:00:00",
         "location_description": "Nashik Toll", "city": "Nashik", "state": "Maharashtra",
         "latitude": "19.9975", "longitude": "73.7898"},
        {"freight_order": fo_del, "event_type": "In Transit",
         "event_datetime": f"{add_days(today(),-4)} 22:00:00",
         "location_description": "Bhopal Bypass", "city": "Bhopal", "state": "Madhya Pradesh",
         "latitude": "23.2599", "longitude": "77.4126"},
        {"freight_order": fo_del, "event_type": "Delivered",
         "event_datetime": f"{add_days(today(),-3)} 16:45:00",
         "location_description": "Delhi Gateway Warehouse", "city": "New Delhi", "state": "Delhi",
         "latitude": "28.6139", "longitude": "77.2090"},
        {"freight_order": fo_it, "event_type": "Dispatched",
         "event_datetime": f"{add_days(today(),-2)} 07:00:00",
         "location_description": "Delhi Gateway", "city": "New Delhi", "state": "Delhi",
         "latitude": "28.6139", "longitude": "77.2090"},
        {"freight_order": fo_it, "event_type": "In Transit",
         "event_datetime": f"{add_days(today(),-1)} 10:30:00",
         "location_description": "Nagpur Ring Road", "city": "Nagpur", "state": "Maharashtra",
         "latitude": "21.1458", "longitude": "79.0882"},
    ]
    for te in tracking_events:
        frappe.get_doc({"doctype": "Shipment Tracking Event",
                        "naming_series": "STE-.YYYY.-.#####", **te}).insert(ignore_permissions=True)

    # ── E-Way Bills ─────────────────────────────────────────────────────────
    ewbs = [
        {"naming_series": "EWB-.YYYY.-.#####", "freight_order": fo_names[0],
         "status": "Delivered", "ewb_number": "1234567890001",
         "generated_date": add_days(today(), -5),
         "valid_upto": add_days(today(), -3),
         "vehicle_number": "MH12AB1234", "hsn_code": "8541",
         "goods_description": "Electronic Components", "invoice_value": 450000,
         "igst_amount": 81000, "transport_mode": "1"},
        {"naming_series": "EWB-.YYYY.-.#####", "freight_order": fo_names[1],
         "status": "Generated", "ewb_number": "1234567890002",
         "generated_date": add_days(today(), -2),
         "valid_upto": add_days(today(), 1),
         "vehicle_number": "DL01GH5678", "hsn_code": "3004",
         "goods_description": "Pharmaceutical Products", "invoice_value": 680000,
         "igst_amount": 122400, "transport_mode": "1"},
        {"naming_series": "EWB-.YYYY.-.#####", "freight_order": fo_names[5],
         "status": "Delivered", "ewb_number": "1234567890003",
         "generated_date": add_days(today(), -10),
         "valid_upto": add_days(today(), -8),
         "vehicle_number": "MH12AB1234", "hsn_code": "2814",
         "goods_description": "Chemical Drums", "invoice_value": 195000,
         "igst_amount": 35100, "transport_mode": "1"},
    ]
    for ewb in ewbs:
        frappe.get_doc({"doctype": "E Way Bill", **ewb}).insert(ignore_permissions=True)

    # ── Customer Complaints — required: complaint_type, customer, complaint_date, complaint_description
    complaints = [
        {"naming_series": "CC-.YYYY.-.#####", "freight_order": fo_names[0],
         "customer": _cust("Acme Electronics Pvt Ltd"),
         "complaint_type": "Delivery Delay", "resolution_status": "Resolved",
         "complaint_date": add_days(today(), -3),
         "complaint_description": "Consignment reached 4 hours late. SLA breach.",
         "resolution_notes": "Traffic jam on NH-44. Compensated with discount on next order."},
        {"naming_series": "CC-.YYYY.-.#####", "freight_order": fo_names[5],
         "customer": _cust("Acme Electronics Pvt Ltd"),
         "complaint_type": "Damaged Goods", "resolution_status": "Open",
         "complaint_date": add_days(today(), -8),
         "complaint_description": "Two chemical drums found damaged on arrival at Mumbai Hub."},
        {"naming_series": "CC-.YYYY.-.#####", "freight_order": fo_names[1],
         "customer": _cust("Bharat Pharma Distributors"),
         "complaint_type": "Documentation Error", "resolution_status": "Under Review",
         "complaint_date": add_days(today(), -1),
         "complaint_description": "E-Way Bill details do not match invoice."},
    ]
    for cc in complaints:
        frappe.get_doc({"doctype": "Customer Complaint", **cc}).insert(ignore_permissions=True)

    # ── Fuel Logs — required: log_date, vehicle, fuel_station, quantity_litres, odometer_reading_km
    fuel_logs = [
        {"naming_series": "FL-.YYYY.-.#####", "vehicle": "MH-12-AB-1234",
         "driver": _drv("Ramesh Kumar Singh"), "log_date": add_days(today(), -5),
         "fuel_station": "Indian Oil, Nasik", "quantity_litres": 180,
         "rate_per_litre": 95.50, "odometer_reading_km": 48000, "fuel_type": "Diesel"},
        {"naming_series": "FL-.YYYY.-.#####", "vehicle": "DL-01-GH-5678",
         "driver": _drv("Suresh Prasad Yadav"), "log_date": add_days(today(), -2),
         "fuel_station": "HP Petrol, Agra Highway", "quantity_litres": 240,
         "rate_per_litre": 96.00, "odometer_reading_km": 81200, "fuel_type": "Diesel"},
        {"naming_series": "FL-.YYYY.-.#####", "vehicle": "MH-14-IJ-7890",
         "driver": _drv("Arun Gawde"), "log_date": today(),
         "fuel_station": "BPCL, Lonavala", "quantity_litres": 35,
         "rate_per_litre": 95.80, "odometer_reading_km": 8850, "fuel_type": "Diesel"},
        {"naming_series": "FL-.YYYY.-.#####", "vehicle": "TN-22-EF-3456",
         "driver": _drv("Muthu Selvam"), "log_date": add_days(today(), -1),
         "fuel_station": "Indian Oil, Vellore", "quantity_litres": 120,
         "rate_per_litre": 94.50, "odometer_reading_km": 55100, "fuel_type": "Diesel"},
        {"naming_series": "FL-.YYYY.-.#####", "vehicle": "KA-09-CD-9012",
         "driver": _drv("Vijay Krishnamurthy"), "log_date": add_days(today(), -3),
         "fuel_station": "Reliance Petro, Tumkur Road", "quantity_litres": 100,
         "rate_per_litre": 95.20, "odometer_reading_km": 22200, "fuel_type": "Diesel"},
    ]
    for fl in fuel_logs:
        frappe.get_doc({"doctype": "Fuel Log", **fl}).insert(ignore_permissions=True)

    # ── Advance Payment Requests — required: request_date, payment_type, requested_amount
    aprs = [
        {"naming_series": "APR-.YYYY.-.#####",
         "request_date": add_days(today(), -5),
         "payment_type": "Driver Advance", "payee_type": "Driver",
         "payee_name": "Ramesh Kumar Singh",
         "driver": _drv("Ramesh Kumar Singh"),
         "requested_amount": 8000, "approved_amount": 8000,
         "purpose": "Fuel & Toll for Mumbai-Delhi run", "status": "Approved"},
        {"naming_series": "APR-.YYYY.-.#####",
         "request_date": add_days(today(), -2),
         "payment_type": "Driver Advance", "payee_type": "Driver",
         "payee_name": "Suresh Prasad Yadav",
         "driver": _drv("Suresh Prasad Yadav"),
         "requested_amount": 12000, "approved_amount": 10000,
         "purpose": "Fuel, Toll, Driver allowance for Delhi-Bengaluru", "status": "Approved"},
        {"naming_series": "APR-.YYYY.-.#####",
         "request_date": today(),
         "payment_type": "Driver Advance", "payee_type": "Driver",
         "payee_name": "Arun Gawde",
         "driver": _drv("Arun Gawde"),
         "requested_amount": 2500,
         "purpose": "Mumbai-Pune run expenses", "status": "Pending Approval"},
        {"naming_series": "APR-.YYYY.-.#####",
         "request_date": add_days(today(), -8),
         "payment_type": "Driver Advance", "payee_type": "Driver",
         "payee_name": "Muthu Selvam",
         "driver": _drv("Muthu Selvam"),
         "requested_amount": 6000, "approved_amount": 6000,
         "purpose": "Chennai-Hyderabad trip advance", "status": "Disbursed"},
    ]
    for apr in aprs:
        frappe.get_doc({"doctype": "Advance Payment Request", **apr}).insert(ignore_permissions=True)

    # ── Dock Appointments — required: appointment_type, warehouse, scheduled_date
    docks = [
        {"naming_series": "DA-.YYYY.-.#####",
         "appointment_type": "Outbound", "warehouse": "Mumbai Hub",
         "vehicle": "MH-12-AB-1234", "driver": _drv("Ramesh Kumar Singh"),
         "scheduled_date": add_days(today(), 1),
         "scheduled_start_time": "09:00:00",
         "status": "Scheduled", "dock_number": "Dock-3"},
        {"naming_series": "DA-.YYYY.-.#####",
         "appointment_type": "Inbound", "warehouse": "Delhi Gateway",
         "vehicle": "DL-01-GH-5678", "driver": _drv("Suresh Prasad Yadav"),
         "scheduled_date": add_days(today(), 1),
         "scheduled_start_time": "14:00:00",
         "status": "Scheduled", "dock_number": "Dock-1"},
        {"naming_series": "DA-.YYYY.-.#####",
         "appointment_type": "Outbound", "warehouse": "Bengaluru Cross-Dock",
         "vehicle": "KA-09-CD-9012", "driver": _drv("Vijay Krishnamurthy"),
         "scheduled_date": today(),
         "scheduled_start_time": "11:00:00",
         "status": "In Progress", "dock_number": "Dock-2"},
        {"naming_series": "DA-.YYYY.-.#####",
         "appointment_type": "Inbound", "warehouse": "Chennai Port Facility",
         "vehicle": "TN-22-EF-3456", "driver": _drv("Muthu Selvam"),
         "scheduled_date": add_days(today(), 2),
         "scheduled_start_time": "08:00:00",
         "status": "Scheduled", "dock_number": "Dock-1"},
    ]
    for da in docks:
        frappe.get_doc({"doctype": "Dock Appointment", **da}).insert(ignore_permissions=True)

    frappe.db.commit()
    print("✅ Transactional demo data installed successfully!")
    print(f"   Freight Orders:      {len(fo_names)}")
    print(f"   Tracking Events:     {len(tracking_events)}")
    print(f"   E-Way Bills:         {len(ewbs)}")
    print(f"   Complaints:          {len(complaints)}")
    print(f"   Fuel Logs:           {len(fuel_logs)}")
    print(f"   Advance Payments:    {len(aprs)}")
    print(f"   Dock Appointments:   {len(docks)}")


def _drv(full_name):
    return frappe.db.get_value("Driver", {"full_name": full_name}, "name") or full_name


def _cust(customer_name):
    return frappe.db.get_value("Customer", {"customer_name": customer_name}, "name") or customer_name
