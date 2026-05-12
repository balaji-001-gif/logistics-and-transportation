"""
Demo Data Installer for Logistics & Transportation ERP
Run via: bench --site [site] execute logistics_transport_erp.logistics_transportation.demo_data.install_demo_data
"""
import frappe
from frappe.utils import today, add_days, add_months


def install_demo_data():
    frappe.set_user("Administrator")

    # 1. Vehicle Types
    vehicle_types = [
        {"type_name": "20 Ft Container", "max_payload_kg": 8000, "max_volume_cbm": 30},
        {"type_name": "32 Ft SXL", "max_payload_kg": 15000, "max_volume_cbm": 55},
        {"type_name": "40 Ft HXL", "max_payload_kg": 22000, "max_volume_cbm": 80},
        {"type_name": "Mini Truck (Tata Ace)", "max_payload_kg": 750, "max_volume_cbm": 6},
        {"type_name": "14 Ft Closed Body", "max_payload_kg": 4000, "max_volume_cbm": 20},
        {"type_name": "Tanker (Liquid)", "max_payload_kg": 18000, "max_volume_cbm": 0},
    ]
    for vt in vehicle_types:
        if not frappe.db.exists("Vehicle Type", vt["type_name"]):
            frappe.get_doc({"doctype": "Vehicle Type", **vt}).insert(ignore_permissions=True)

    # 2. Warehouses — required: warehouse_name, address_line_1, city, state
    warehouses = [
        {"warehouse_name": "Mumbai Hub", "address_line_1": "Plot 12, JNPT Road, Nhava Sheva",
         "city": "Mumbai", "state": "Maharashtra", "pincode": "400707", "warehouse_type": "Owned"},
        {"warehouse_name": "Delhi Gateway", "address_line_1": "NH-44, Kundli Industrial Area",
         "city": "New Delhi", "state": "Delhi", "pincode": "131028", "warehouse_type": "Owned"},
        {"warehouse_name": "Bengaluru Cross-Dock", "address_line_1": "Sy No 45, Hoskote Industrial Area",
         "city": "Bengaluru", "state": "Karnataka", "pincode": "562114", "warehouse_type": "Cross-Dock"},
        {"warehouse_name": "Chennai Port Facility", "address_line_1": "Anna Salai, Royapuram",
         "city": "Chennai", "state": "Tamil Nadu", "pincode": "600013", "warehouse_type": "Bonded"},
        {"warehouse_name": "Pune Spoke", "address_line_1": "Bhosari MIDC, Phase II",
         "city": "Pune", "state": "Maharashtra", "pincode": "411026", "warehouse_type": "Leased"},
        {"warehouse_name": "Hyderabad Spoke", "address_line_1": "Patancheru Industrial Area, IDA",
         "city": "Hyderabad", "state": "Telangana", "pincode": "502319", "warehouse_type": "3PL"},
    ]
    for w in warehouses:
        if not frappe.db.exists("Warehouse", w["warehouse_name"]):
            frappe.get_doc({"doctype": "Warehouse", **w}).insert(ignore_permissions=True)

    # 3. Vehicles
    vehicles = [
        {"registration_number": "MH-12-AB-1234", "vehicle_type": "32 Ft SXL", "status": "Available",
         "make": "Tata", "model": "Prima 4028.S", "year_of_manufacture": 2021,
         "fuel_type": "Diesel", "payload_capacity_kg": 15000, "current_odometer_km": 48200,
         "next_service_km": 50000, "next_service_date": add_days(today(), 12),
         "ownership_type": "Owned", "home_warehouse": "Mumbai Hub"},
        {"registration_number": "DL-01-GH-5678", "vehicle_type": "40 Ft HXL", "status": "Available",
         "make": "Ashok Leyland", "model": "Captain 4940", "year_of_manufacture": 2020,
         "fuel_type": "Diesel", "payload_capacity_kg": 22000, "current_odometer_km": 81500,
         "next_service_km": 85000, "next_service_date": add_days(today(), 20),
         "ownership_type": "Owned", "home_warehouse": "Delhi Gateway"},
        {"registration_number": "KA-09-CD-9012", "vehicle_type": "20 Ft Container", "status": "Available",
         "make": "Eicher", "model": "Pro 6031", "year_of_manufacture": 2022,
         "fuel_type": "Diesel", "payload_capacity_kg": 8000, "current_odometer_km": 22400,
         "next_service_km": 25000, "next_service_date": add_days(today(), 30),
         "ownership_type": "Owned", "home_warehouse": "Bengaluru Cross-Dock"},
        {"registration_number": "TN-22-EF-3456", "vehicle_type": "14 Ft Closed Body", "status": "On Trip",
         "make": "Mahindra", "model": "Furio 7", "year_of_manufacture": 2021,
         "fuel_type": "Diesel", "payload_capacity_kg": 4000, "current_odometer_km": 55300,
         "next_service_km": 60000, "next_service_date": add_days(today(), 25),
         "ownership_type": "Owned", "home_warehouse": "Chennai Port Facility"},
        {"registration_number": "MH-14-IJ-7890", "vehicle_type": "Mini Truck (Tata Ace)", "status": "Available",
         "make": "Tata", "model": "Ace Gold", "year_of_manufacture": 2023,
         "fuel_type": "Diesel", "payload_capacity_kg": 750, "current_odometer_km": 8900,
         "next_service_km": 10000, "next_service_date": add_days(today(), 45),
         "ownership_type": "Owned", "home_warehouse": "Pune Spoke"},
        {"registration_number": "TS-09-KL-2345", "vehicle_type": "32 Ft SXL", "status": "Under Maintenance",
         "make": "BharatBenz", "model": "2523R", "year_of_manufacture": 2019,
         "fuel_type": "Diesel", "payload_capacity_kg": 13000, "current_odometer_km": 120000,
         "next_service_km": 125000, "next_service_date": add_days(today(), 5),
         "ownership_type": "Owned", "home_warehouse": "Hyderabad Spoke"},
    ]
    for v in vehicles:
        if not frappe.db.exists("Vehicle", v["registration_number"]):
            doc = frappe.get_doc({"doctype": "Vehicle", **v})
            doc.append("documents", {"document_type": "Registration Certificate (RC)", "expiry_date": add_days(today(), 365)})
            doc.append("documents", {"document_type": "Insurance", "expiry_date": add_days(today(), 180)})
            doc.append("documents", {"document_type": "Fitness Certificate", "expiry_date": add_days(today(), 240)})
            doc.insert(ignore_permissions=True)

    # 4. Drivers
    drivers = [
        {"naming_series": "DRV-.YYYY.-.####", "full_name": "Ramesh Kumar Singh",
         "status": "Active", "mobile_number": "9876543210", "primary_dl_number": "MH0120210012345",
         "dl_expiry_date": add_months(today(), 24), "dl_class": "HMV",
         "date_of_birth": "1985-06-15", "blood_group": "B+",
         "home_warehouse": "Mumbai Hub"},
        {"naming_series": "DRV-.YYYY.-.####", "full_name": "Suresh Prasad Yadav",
         "status": "Active", "mobile_number": "9845678901", "primary_dl_number": "DL0220180023456",
         "dl_expiry_date": add_months(today(), 18), "dl_class": "HMV",
         "date_of_birth": "1980-03-22", "blood_group": "O+",
         "home_warehouse": "Delhi Gateway"},
        {"naming_series": "DRV-.YYYY.-.####", "full_name": "Vijay Krishnamurthy",
         "status": "Active", "mobile_number": "9731234567", "primary_dl_number": "KA0920190034567",
         "dl_expiry_date": add_months(today(), 30), "dl_class": "HMV",
         "date_of_birth": "1990-11-08", "blood_group": "A+",
         "home_warehouse": "Bengaluru Cross-Dock"},
        {"naming_series": "DRV-.YYYY.-.####", "full_name": "Muthu Selvam",
         "status": "Active", "mobile_number": "9600112233", "primary_dl_number": "TN2220200045678",
         "dl_expiry_date": add_months(today(), 12), "dl_class": "HMV",
         "date_of_birth": "1988-07-30", "blood_group": "AB+",
         "home_warehouse": "Chennai Port Facility"},
        {"naming_series": "DRV-.YYYY.-.####", "full_name": "Arun Gawde",
         "status": "Active", "mobile_number": "9765432109", "primary_dl_number": "MH1420220056789",
         "dl_expiry_date": add_months(today(), 36), "dl_class": "LMV",
         "date_of_birth": "1995-02-14", "blood_group": "O-",
         "home_warehouse": "Pune Spoke"},
        {"naming_series": "DRV-.YYYY.-.####", "full_name": "Srinivas Reddy",
         "status": "Active", "mobile_number": "9912345678", "primary_dl_number": "TS0920210067890",
         "dl_expiry_date": add_months(today(), 20), "dl_class": "HMV",
         "date_of_birth": "1983-09-05", "blood_group": "B-",
         "home_warehouse": "Hyderabad Spoke"},
        {"naming_series": "DRV-.YYYY.-.####", "full_name": "Devendra Patel",
         "status": "On Leave", "mobile_number": "9823456789", "primary_dl_number": "MH1220190078901",
         "dl_expiry_date": add_months(today(), 8), "dl_class": "HMV",
         "date_of_birth": "1978-12-20", "blood_group": "A-",
         "home_warehouse": "Mumbai Hub"},
    ]
    for d in drivers:
        if not frappe.db.exists("Driver", {"full_name": d["full_name"]}):
            frappe.get_doc({"doctype": "Driver", **d}).insert(ignore_permissions=True)

    # 5. Route Masters
    routes = [
        {"route_name": "Mumbai - Delhi", "origin_city": "Mumbai", "destination_city": "New Delhi",
         "origin_state": "Maharashtra", "destination_state": "Delhi",
         "distance_km": 1415, "estimated_transit_days": 2, "route_type": "National Highway",
         "is_interstate": 1, "is_active": 1},
        {"route_name": "Mumbai - Pune", "origin_city": "Mumbai", "destination_city": "Pune",
         "origin_state": "Maharashtra", "destination_state": "Maharashtra",
         "distance_km": 148, "estimated_transit_days": 1, "route_type": "National Highway",
         "is_interstate": 0, "is_active": 1},
        {"route_name": "Delhi - Bengaluru", "origin_city": "New Delhi", "destination_city": "Bengaluru",
         "origin_state": "Delhi", "destination_state": "Karnataka",
         "distance_km": 2150, "estimated_transit_days": 3, "route_type": "National Highway",
         "is_interstate": 1, "is_active": 1},
        {"route_name": "Chennai - Hyderabad", "origin_city": "Chennai", "destination_city": "Hyderabad",
         "origin_state": "Tamil Nadu", "destination_state": "Telangana",
         "distance_km": 625, "estimated_transit_days": 1, "route_type": "National Highway",
         "is_interstate": 1, "is_active": 1},
        {"route_name": "Bengaluru - Mumbai", "origin_city": "Bengaluru", "destination_city": "Mumbai",
         "origin_state": "Karnataka", "destination_state": "Maharashtra",
         "distance_km": 985, "estimated_transit_days": 2, "route_type": "National Highway",
         "is_interstate": 1, "is_active": 1},
        {"route_name": "Delhi - Jaipur", "origin_city": "New Delhi", "destination_city": "Jaipur",
         "origin_state": "Delhi", "destination_state": "Rajasthan",
         "distance_km": 280, "estimated_transit_days": 1, "route_type": "National Highway",
         "is_interstate": 1, "is_active": 1},
        {"route_name": "Hyderabad - Pune", "origin_city": "Hyderabad", "destination_city": "Pune",
         "origin_state": "Telangana", "destination_state": "Maharashtra",
         "distance_km": 563, "estimated_transit_days": 1, "route_type": "National Highway",
         "is_interstate": 1, "is_active": 1},
    ]
    for r in routes:
        if not frappe.db.exists("Route Master", r["route_name"]):
            frappe.get_doc({"doctype": "Route Master", **r}).insert(ignore_permissions=True)

    # 6. Freight Rate Cards
    rate_cards = [
        {"naming_series": "FRC-.YYYY.-.####", "card_name": "Standard Road FTL 2026",
         "effective_from": "2026-01-01", "is_active": 1, "transport_mode": "Road FTL"},
        {"naming_series": "FRC-.YYYY.-.####", "card_name": "Express LTL Mumbai Zone",
         "effective_from": "2026-01-01", "is_active": 1, "transport_mode": "Road LTL"},
        {"naming_series": "FRC-.YYYY.-.####", "card_name": "South India FTL Rates",
         "effective_from": "2026-03-01", "is_active": 1, "transport_mode": "Road FTL"},
    ]
    for rc in rate_cards:
        if not frappe.db.exists("Freight Rate Card", {"card_name": rc["card_name"]}):
            doc = frappe.get_doc({"doctype": "Freight Rate Card", **rc})
            doc.append("rate_slabs", {"origin": "Mumbai", "destination": "Delhi", "transport_mode": "Road FTL", "rate_amount": 45000})
            doc.append("rate_slabs", {"origin": "Delhi", "destination": "Bengaluru", "transport_mode": "Road FTL", "rate_amount": 68000})
            doc.insert(ignore_permissions=True)

    # 7. Vehicle Maintenance Requests
    vmrs = [
        {"naming_series": "VMR-.YYYY.-.#####", "vehicle": "TS-09-KL-2345",
         "request_date": add_days(today(), -2), "request_type": "Breakdown",
         "priority": "High", "status": "In Progress",
         "odometer_at_request_km": 120000,
         "complaint_description": "Engine overheating issue. Coolant leak detected.",
         "service_vendor": "Sri Balaji Motors, Hyderabad",
         "scheduled_service_date": today(), "labour_cost": 8500},
        {"naming_series": "VMR-.YYYY.-.#####", "vehicle": "MH-12-AB-1234",
         "request_date": add_days(today(), -15), "request_type": "Preventive Maintenance",
         "priority": "Medium", "status": "Completed",
         "odometer_at_request_km": 45000,
         "complaint_description": "Scheduled 45,000 km service. Oil change, filter replacement.",
         "service_vendor": "Tata Authorized Service, Mumbai",
         "scheduled_service_date": add_days(today(), -14),
         "completed_date": add_days(today(), -14),
         "labour_cost": 6000, "total_maintenance_cost": 12500,
         "resolution_notes": "Engine oil replaced, air and fuel filters changed. Brakes adjusted."},
        {"naming_series": "VMR-.YYYY.-.#####", "vehicle": "KA-09-CD-9012",
         "request_date": add_days(today(), -5), "request_type": "Tyre Change",
         "priority": "Medium", "status": "Completed",
         "odometer_at_request_km": 22000,
         "complaint_description": "Front left tyre worn beyond limit.",
         "service_vendor": "MRF Tyre Center, Bengaluru",
         "completed_date": add_days(today(), -4),
         "labour_cost": 500, "total_maintenance_cost": 8500,
         "resolution_notes": "MRF ZLX 10.00-20 tyre replaced."},
        {"naming_series": "VMR-.YYYY.-.#####", "vehicle": "DL-01-GH-5678",
         "request_date": today(), "request_type": "Preventive Maintenance",
         "priority": "Low", "status": "Open",
         "odometer_at_request_km": 81500,
         "complaint_description": "[AUTO] Predictive Maintenance Alert. Odometer 81500 km — service due at 85000 km.",
         "service_vendor": "Ashok Leyland Service, Delhi"},
    ]
    for vmr in vmrs:
        doc = frappe.get_doc({"doctype": "Vehicle Maintenance Request", **vmr})
        doc.insert(ignore_permissions=True)

    frappe.db.commit()
    print("✅ Demo data installed successfully!")
    print(f"   Vehicle Types: {len(vehicle_types)}")
    print(f"   Warehouses:    {len(warehouses)}")
    print(f"   Vehicles:      {len(vehicles)}")
    print(f"   Drivers:       {len(drivers)}")
    print(f"   Routes:        {len(routes)}")
    print(f"   Rate Cards:    {len(rate_cards)}")
    print(f"   VMRs:          {len(vmrs)}")
