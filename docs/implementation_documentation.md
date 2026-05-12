# Logistics & Transportation ERP — Complete Implementation Documentation

**Project:** Logistics & Transportation ERP (Frappe/ERPNext v15)  
**Repository:** https://github.com/balaji-001-gif/logistics-and-transportation.git  
**App Name:** `logistics_transport_erp`  
**Module:** `Logistics Transportation`  
**Framework:** Frappe v15 / ERPNext  
**Date:** May 2026

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Initial Audit — Before State](#initial-audit--before-state)
3. [Implementation Plan](#implementation-plan)
4. [Feature 1 — Logistics Settings & Configuration](#feature-1--logistics-settings--configuration)
5. [Feature 2 — Vahan/Sarathi Government API Integration](#feature-2--vahansarathi-government-api-integration)
6. [Feature 3 — Predictive Maintenance Scheduler](#feature-3--predictive-maintenance-scheduler)
7. [Feature 4 — NIC E-Way Bill API Automation](#feature-4--nic-e-way-bill-api-automation)
8. [Feature 5 — GPS Route Mapping & Driver Portal](#feature-5--gps-route-mapping--driver-portal)
9. [Reports & Analytics](#reports--analytics)
10. [Notifications System](#notifications-system)
11. [Management Workspace](#management-workspace)
12. [Complete File Inventory](#complete-file-inventory)
13. [Deployment Guide](#deployment-guide)
14. [Configuration Reference](#configuration-reference)

---

## Executive Summary

The Logistics & Transportation ERP was audited and found to have a solid operational core — covering freight settlement, trip sheets, and consignment tracking. However, it lacked the technological integration required for a modern, production-grade logistics platform.

This implementation transforms the ERP with:

| Feature | Status |
|---|---|
| Centralized API Settings (Logistics Settings) | ✅ Implemented |
| Vahan/Sarathi Government API for RC & DL Verification | ✅ Implemented |
| Predictive Maintenance Scheduler | ✅ Implemented |
| NIC E-Way Bill API Automation | ✅ Implemented |
| Google Maps GPS Route Mapping | ✅ Implemented |
| Driver Mobile Portal | ✅ Implemented |
| Vehicle Profitability Report | ✅ Implemented |
| Driver Trip Summary Report | ✅ Implemented |
| Automated Notifications (RC Expiry, Maintenance) | ✅ Implemented |
| Management Workspace Dashboard | ✅ Implemented |

---

## Initial Audit — Before State

### Repository Structure (Before)

```
logistics-and-transportation/
├── logistics_transport_erp/
│   ├── hooks.py
│   ├── install.py
│   ├── logistics_transportation/
│   │   └── doctype/
│   │       ├── vehicle/
│   │       ├── driver/
│   │       ├── freight_order/
│   │       ├── trip_sheet/
│   │       ├── e_way_bill/
│   │       ├── route_master/
│   │       ├── shipment_tracking_event/
│   │       ├── vehicle_maintenance_request/
│   │       └── [12 more DocTypes]
└── pyproject.toml
```

### Findings

#### ✅ Strengths (Already Present)
- **16 DocTypes** covering the full logistics lifecycle
- Freight Order with GST calculations (CGST/SGST/IGST)
- Trip Sheet with Toll & Fuel tracking
- Shipment Tracking Events for real-time status updates
- Vehicle Maintenance Request with parts tracking
- E-Way Bill DocType with expiry alerts
- Driver DL expiry validation
- Customer Contract & Rate Card management
- Freight Settlement & Invoice generation
- Load Planning module

#### ❌ Gaps Identified
- No government API integration (Vahan, Sarathi, NIC)
- No GPS/GIS capabilities on any form
- No predictive maintenance automation
- No centralized API settings management
- No mobile portal for field drivers
- No management dashboard/workspace
- No analytical reports (profitability, driver KPIs)
- Scheduler tasks registered but `tasks.py` was empty
- Route Master had no geocoding capability

---

## Implementation Plan

Five major feature streams were identified and executed:

```
Stream 1: Logistics Settings DocType (Foundation for all API config)
    │
    ├── Stream 2: Vahan/Sarathi API (RC & DL Compliance)
    ├── Stream 3: Predictive Maintenance (Daily scheduler)
    ├── Stream 4: NIC E-Way Bill API (EWB generation)
    └── Stream 5: GPS + Driver Portal (Maps & Mobile)
                      │
                      ├── Reports (Profitability, Driver KPIs)
                      ├── Notifications (RC Expiry, Maintenance)
                      └── Workspace (Management Dashboard)
```

---

## Feature 1 — Logistics Settings & Configuration

### Purpose
A centralized singleton DocType to manage all API credentials and operational thresholds from one place — eliminating hardcoded values across the codebase.

### Files Created/Modified

| File | Action |
|---|---|
| `doctype/logistics_settings/logistics_settings.json` | NEW — DocType definition |
| `doctype/logistics_settings/logistics_settings.py` | NEW — Python class |
| `doctype/logistics_settings/logistics_settings.js` | NEW — Frontend JS |
| `hooks.py` | MODIFIED — Added to fixtures |

### DocType Fields

| Field | Type | Purpose |
|---|---|---|
| `nic_api_environment` | Select | Sandbox / Production toggle |
| `nic_gstin` | Data | Company GSTIN for NIC APIs |
| `nic_username` | Data | NIC portal login |
| `nic_password` | **Password** | Encrypted NIC credential |
| `vahan_api_key` | **Password** | Encrypted Vahan/Sarathi API key |
| `vahan_api_enabled` | Check | Master toggle for compliance enforcement |
| `google_maps_api_key` | **Password** | Encrypted Google Maps key |
| `maps_enabled` | Check | Toggle map panels on forms |
| `maintenance_alert_days` | Int | Days before service → trigger VMR (default: 7) |
| `maintenance_alert_km` | Int | KM gap before service → trigger VMR (default: 500) |
| `ewb_expiry_alert_hours` | Int | Hours before EWB expiry → alert (default: 6) |

> **Security Note:** All API keys use `fieldtype: "Password"` — Frappe encrypts these at rest using AES-256.

---

## Feature 2 — Vahan/Sarathi Government API Integration

### Purpose
Automated real-time verification of vehicle Registration Certificates (RC) and driver Driving Licences (DL) against government databases. Blocks trip dispatch if compliance fails.

### Architecture

```
Vehicle Form                   Driver Form
     │                              │
[Verify RC Button]         [Verify DL Button]
     │                              │
     ▼                              ▼
vehicle.py::verify_rc()    driver.py::verify_dl()
     │                              │
     └──────────┬───────────────────┘
                ▼
        api/vahan_api.py
                │
        ┌───────┴────────┐
        │  check_rc_status()      │
        │  check_dl_status()      │
        └───────┬────────┘
                ▼
        NIC Vahan/Sarathi API
        (Sandbox or Production)
```

### Files Created/Modified

| File | Action | Description |
|---|---|---|
| `api/vahan_api.py` | **NEW** | Core API wrapper with fallback handling |
| `api/__init__.py` | **NEW** | Package init |
| `doctype/vehicle/vehicle.json` | MODIFIED | Added rc_status, rc_fitness_upto, rc_owner_name, rc_verified_on fields |
| `doctype/vehicle/vehicle.py` | MODIFIED | Added `verify_rc()` + `verify_vehicle_rc()` whitelist endpoint |
| `doctype/vehicle/vehicle.js` | MODIFIED | Added "Verify RC (Vahan)" button + colour indicators |
| `doctype/driver/driver.json` | MODIFIED | Added dl_verified_status, dl_valid_upto, dl_verified_class, dl_verified_on, current_vehicle fields |
| `doctype/driver/driver.py` | MODIFIED | Added `verify_dl()` + `verify_driver_dl()` whitelist endpoint |
| `doctype/driver/driver.js` | MODIFIED | Added "Verify DL (Sarathi)" button + colour indicators |
| `doctype/trip_sheet/trip_sheet.py` | MODIFIED | Added `check_compliance_before_dispatch()` submission guard |

### New Fields on Vehicle

| Field | Type | Description |
|---|---|---|
| `rc_status` | Data (read-only) | Active / Expired / Unknown |
| `rc_fitness_upto` | Date (read-only) | Fitness validity date |
| `rc_owner_name` | Data (read-only) | Registered owner from Vahan |
| `rc_verified_on` | Datetime (read-only) | Last verification timestamp |

### New Fields on Driver

| Field | Type | Description |
|---|---|---|
| `dl_verified_status` | Data (read-only) | Active / Expired / Unknown |
| `dl_valid_upto` | Date (read-only) | DL validity from Sarathi |
| `dl_verified_class` | Data (read-only) | Vehicle class from Sarathi |
| `dl_verified_on` | Datetime (read-only) | Last verification timestamp |
| `current_vehicle` | Link → Vehicle | Auto-set on Trip Sheet submission |

### Compliance Guard Logic (`trip_sheet.py`)

```python
def check_compliance_before_dispatch(self):
    settings = frappe.get_single("Logistics Settings")
    if not settings.vahan_api_enabled:
        return  # Skip if API is disabled
    
    # Block if Vehicle RC is not Active
    if self.vehicle:
        rc_status = frappe.db.get_value("Vehicle", self.vehicle, "rc_status")
        if rc_status not in ("Active", "API Disabled"):
            frappe.throw("Vehicle RC status is invalid...")
    
    # Block if Driver DL is not Active
    if self.driver:
        dl_status = frappe.db.get_value("Driver", self.driver, "dl_verified_status")
        if dl_status not in ("Active", "API Disabled"):
            frappe.throw("Driver DL status is invalid...")
```

---

## Feature 3 — Predictive Maintenance Scheduler

### Purpose
A daily automated scheduler that proactively monitors vehicle service thresholds and creates maintenance requests before breakdowns occur.

### Files Created/Modified

| File | Action | Description |
|---|---|---|
| `tasks.py` | **NEW** | All scheduler functions |
| `doctype/vehicle/vehicle.json` | MODIFIED | Added `maintenance_alert_sent_on` (hidden Date field) |
| `hooks.py` | MODIFIED | Registered daily scheduler events |
| `notification/vehicle_maintenance_due_auto/` | **NEW** | Email notification for auto-VMR creation |

### Scheduler Logic Flow

```
Daily at midnight (Frappe Scheduler)
         │
         ▼
tasks.auto_maintenance_check()
         │
         ├── Fetch all Active/On Trip vehicles
         │
         ├── For each vehicle:
         │   ├── Check: current_odometer >= (next_service_km - alert_km_threshold)
         │   ├── Check: today >= (next_service_date - alert_days_threshold)
         │   └── Skip if already alerted today (maintenance_alert_sent_on)
         │
         ├── If threshold hit:
         │   ├── Create Vehicle Maintenance Request (status: Open, priority: High)
         │   ├── Set maintenance_alert_sent_on = today
         │   └── Notify Fleet Manager via realtime + email
         │
         └── Commit to DB
```

### Maintenance Alert Thresholds

| Setting | Default | Description |
|---|---|---|
| `maintenance_alert_days` | 7 days | Days before service date |
| `maintenance_alert_km` | 500 km | KM gap before next service KM |

### Daily E-Way Bill Expiry Check

Also runs daily via `tasks.check_ewb_expiry()`:
- Fetches all EWBs expiring within `ewb_expiry_alert_hours`
- Sends real-time notification to all users

---

## Feature 4 — NIC E-Way Bill API Automation

### Purpose
Direct integration with the GST/NIC E-Way Bill portal to generate EWBs programmatically, eliminating manual portal entry.

### API Flow

```
E Way Bill Form
      │
[Generate E-Way Bill (NIC API)]
      │
      ▼
e_way_bill.py::generate_e_way_bill()
      │
      ▼
api/ewb_api.py::generate_ewb()
      │
      ├── Get/refresh auth token (_get_auth_token)
      │   └── Cached for 5.5 hours (NIC TTL = 6h)
      │
      ├── Build payload (_build_ewb_payload)
      │   └── Maps DocType fields → NIC JSON schema
      │
      ├── POST to NIC API endpoint
      │   └── Auto-retry on 401 (token expired)
      │
      └── Save EWB Number + Valid Upto to document
```

### Files Created/Modified

| File | Action | Description |
|---|---|---|
| `api/ewb_api.py` | **NEW** | Full NIC EWB API wrapper with token caching |
| `doctype/e_way_bill/e_way_bill.py` | MODIFIED | Added `generate_ewb_via_api()` + whitelist endpoint |
| `doctype/e_way_bill/e_way_bill.js` | MODIFIED | Added "Generate E-Way Bill (NIC API)" button |

### NIC API Endpoints

| Environment | Base URL |
|---|---|
| Sandbox | `https://einvoice1-sandbox.nic.in/EWB/ewbapi` |
| Production | `https://einvapi.nic.in/EWB/ewbapi` |

### EWB Payload Mapping

| ERP Field | NIC API Field |
|---|---|
| `invoice_value` | `totalValue` |
| `cgst_amount` | `cgstValue` |
| `igst_amount` | `igstValue` |
| `vehicle_number` | `vehicleNo` |
| `lr_number` | `transDocNo` |
| `hsn_code` | `hsnCode` |
| `consignee_gstin` | `toGstin` |

---

## Feature 5 — GPS Route Mapping & Driver Portal

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                 Google Maps Integration              │
├──────────────┬──────────────────────────────────────┤
│  Frontend    │  public/js/route_map.js               │
│  (Browser)   │  LogisticsRouteMap.render(frm, opts)  │
├──────────────┼──────────────────────────────────────┤
│  Backend     │  api/maps_api.py                      │
│  (Python)    │  get_maps_api_key()                   │
│              │  geocode_city()                       │
│              │  get_route_distance()                 │
└──────────────┴──────────────────────────────────────┘
```

### Files Created/Modified

| File | Action | Description |
|---|---|---|
| `api/maps_api.py` | **NEW** | Google Maps API backend wrapper |
| `public/js/route_map.js` | **NEW** | Reusable map component for Frappe forms |
| `doctype/route_master/route_master.json` | MODIFIED | Added lat_origin, lng_origin, lat_destination, lng_destination, route_map_html |
| `doctype/route_master/route_master.py` | MODIFIED | Added `fetch_coordinates_from_api()` + whitelist endpoint |
| `doctype/route_master/route_master.js` | MODIFIED | Added "Fetch Coordinates & Distance" button + map render |
| `doctype/freight_order/freight_order.json` | MODIFIED | Added `route_map_html` field |
| `doctype/freight_order/freight_order.js` | MODIFIED | Renders route map with live tracking pins |
| `doctype/trip_sheet/trip_sheet.json` | MODIFIED | Added `route_map_html` field |
| `doctype/trip_sheet/trip_sheet.js` | MODIFIED | Renders route map for the trip |
| `doctype/shipment_tracking_event/shipment_tracking_event.py` | MODIFIED | Added reverse geocoding |
| `page/driver_portal/driver_portal.json` | **NEW** | Frappe Page definition |
| `page/driver_portal/driver_portal.html` | **NEW** | Mobile-first HTML template |
| `page/driver_portal/driver_portal.js` | **NEW** | Portal logic with GPS capture |
| `page/driver_portal/driver_portal.css` | **NEW** | Dark-mode mobile CSS |
| `api/driver_portal_api.py` | **NEW** | Backend API for portal actions |

### New Fields on Route Master

| Field | Type | Description |
|---|---|---|
| `lat_origin` | Float | Geocoded origin latitude |
| `lng_origin` | Float | Geocoded origin longitude |
| `lat_destination` | Float | Geocoded destination latitude |
| `lng_destination` | Float | Geocoded destination longitude |
| `route_map_html` | HTML | Embedded map panel |

### Reverse Geocoding (Tracking Events)
When a driver submits GPS coordinates via the portal, the system automatically reverse-geocodes them to populate `city` and `state` on the Shipment Tracking Event.

### Driver Portal Features

| Feature | Description |
|---|---|
| View Assigned Trips | Lists all Open & In Transit trips for the driver |
| Update Status | One-tap status update (Dispatched, In Transit, Delivered) |
| GPS Capture | Automatically captures browser geolocation |
| Log Expenses | Submit Fuel/Toll expenses that sync to Trip Sheet |

**Portal URL:** `/app/driver-portal`

---

## Reports & Analytics

### Report 1: Vehicle Profitability

**File:** `report/vehicle_profitability/vehicle_profitability.py`  
**Type:** Script Report | **Ref DocType:** Vehicle

**Columns:**

| Column | Description |
|---|---|
| Vehicle | Registration number |
| Revenue (Freight) | Sum of total_amount from submitted Freight Orders |
| Fuel Expense | Sum of total_fuel_amount from submitted Trip Sheets |
| Toll Expense | Sum of total_toll_amount from submitted Trip Sheets |
| Maintenance Cost | Sum of total_maintenance_cost from completed VMRs |
| Net Profit | Revenue − (Fuel + Toll + Maintenance) |
| Margin % | Net Profit ÷ Revenue × 100 |

### Report 2: Driver Trip Summary

**File:** `report/driver_trip_summary/driver_trip_summary.py`  
**Type:** Script Report | **Ref DocType:** Driver

**Columns:**

| Column | Description |
|---|---|
| Driver | Driver name |
| Total Trips | Count of submitted Trip Sheets |
| Total KM Covered | Sum of distance_covered_km |
| Total Fuel (L) | Sum of total_fuel_litres |
| Avg KMPL | Total KM ÷ Total Fuel |
| Advance Taken | Sum of driver_advance_given |

---

## Notifications System

### Notification 1: Vehicle Maintenance Due (Auto)

| Property | Value |
|---|---|
| DocType | Vehicle Maintenance Request |
| Channel | Email + System |
| Recipients | Users with "Fleet Manager" role |
| Trigger | On document creation (auto-created by scheduler) |
| Subject | `Auto-Maintenance Alert: {doc.vehicle}` |

### Notification 2: Vehicle RC Expiry Alert

| Property | Value |
|---|---|
| DocType | Vehicle |
| Channel | Email + System |
| Recipients | Users with "Fleet Manager" role |
| Trigger | When `rc_fitness_upto` is set/updated |
| Subject | `RC Expiry Alert: {doc.registration_number}` |

---

## Management Workspace

**File:** `workspace/logistics_management/logistics_management.json`

The Logistics Management workspace provides a central dashboard with:

### Quick Shortcuts
- Freight Order
- Trip Sheet
- E-Way Bill
- Vehicle
- Driver

### Analytics Links
- Vehicle Profitability Report
- Driver Trip Summary Report

---

## Complete File Inventory

### New Files Created (25 files)

```
logistics_transport_erp/
├── api/
│   ├── __init__.py
│   ├── vahan_api.py                    # Vahan/Sarathi API wrapper
│   ├── ewb_api.py                      # NIC E-Way Bill API wrapper
│   ├── maps_api.py                     # Google Maps API wrapper
│   └── driver_portal_api.py            # Driver Portal backend API
├── tasks.py                            # Scheduler tasks
├── public/
│   └── js/
│       └── route_map.js                # Reusable Google Maps component
└── logistics_transportation/
    ├── doctype/
    │   └── logistics_settings/
    │       ├── __init__.py
    │       ├── logistics_settings.json
    │       ├── logistics_settings.py
    │       └── logistics_settings.js
    ├── notification/
    │   ├── vehicle_maintenance_due_auto/
    │   │   └── vehicle_maintenance_due_auto.json
    │   └── vehicle_rc_expiry_alert/
    │       └── vehicle_rc_expiry_alert.json
    ├── report/
    │   ├── vehicle_profitability/
    │   │   ├── vehicle_profitability.json
    │   │   ├── vehicle_profitability.py
    │   │   └── vehicle_profitability.js
    │   └── driver_trip_summary/
    │       ├── driver_trip_summary.json
    │       └── driver_trip_summary.py
    ├── page/
    │   └── driver_portal/
    │       ├── driver_portal.json
    │       ├── driver_portal.html
    │       ├── driver_portal.js
    │       └── driver_portal.css
    └── workspace/
        └── logistics_management/
            └── logistics_management.json
```

### Modified Files (12 files)

```
logistics_transport_erp/
├── hooks.py                            # + scheduler, fixtures, route rules
└── logistics_transportation/
    └── doctype/
        ├── vehicle/
        │   ├── vehicle.json            # + RC verification fields
        │   ├── vehicle.py              # + verify_rc() method
        │   └── vehicle.js             # + Verify RC button
        ├── driver/
        │   ├── driver.json            # + DL verification + current_vehicle fields
        │   ├── driver.py              # + verify_dl() method
        │   └── driver.js             # + Verify DL button
        ├── trip_sheet/
        │   ├── trip_sheet.json        # + route_map_html field
        │   ├── trip_sheet.py          # + compliance guard + driver status update
        │   └── trip_sheet.js          # + GPS map rendering
        ├── freight_order/
        │   ├── freight_order.json     # + route_map_html field
        │   └── freight_order.js       # + GPS map + tracking pins
        ├── e_way_bill/
        │   ├── e_way_bill.py          # + generate_ewb_via_api()
        │   └── e_way_bill.js          # + Generate EWB button
        ├── route_master/
        │   ├── route_master.json      # + lat/lng GPS fields
        │   ├── route_master.py        # + geocoding methods
        │   └── route_master.js        # + Fetch Coordinates button
        └── shipment_tracking_event/
            └── shipment_tracking_event.py  # + reverse geocoding
```

---

## Deployment Guide

### Step 1: Clean Server Installation

```bash
# Remove any previous failed installation
cd ~/f15-bk
rm -rf apps/logistics_transport_erp
rm -rf apps/logistics-and-transportation

# Get app from GitHub
bench get-app https://github.com/balaji-001-gif/logistics-and-transportation.git
```

### Step 2: Install on Site

```bash
bench --site [your-site-name] install-app logistics_transport_erp
bench --site [your-site-name] migrate
bench build --app logistics_transport_erp
bench restart
```

### Step 3: Configure API Settings

Navigate to **Logistics Management → Logistics Settings** and configure:

```
NIC E-Way Bill API:
  Environment:  Sandbox (for testing) / Production
  GSTIN:        Your company GSTIN (15 digits)
  Username:     NIC portal username
  Password:     NIC portal password

Vahan / Sarathi API:
  API Key:      Your Vahan API Key (from NIC developer portal)
  Enable:       ✅ Check this box to enforce compliance

Google Maps:
  API Key:      Your Google Maps API Key
  Enable:       ✅ Check to show maps on forms

Alert Thresholds:
  Maintenance Alert Days: 7
  Maintenance Alert KM:   500
  EWB Expiry Hours:       6
```

### Step 4: Verify Installation

```bash
# Run maintenance scheduler manually to test
bench --site [site] execute logistics_transport_erp.tasks.auto_maintenance_check

# Check logs for errors
bench --site [site] show-pending-jobs
tail -f logs/frappe.log
```

---

## Configuration Reference

### hooks.py — Registered Events

```python
# Daily scheduler tasks
scheduler_events = {
    "daily": [
        "logistics_transport_erp.tasks.auto_maintenance_check",
        "logistics_transport_erp.tasks.check_ewb_expiry",
    ]
}

# App-wide JS (route_map.js loaded on every page)
app_include_js = [
    "/assets/logistics_transport_erp/js/logistics_transport_erp.js",
    "/assets/logistics_transport_erp/js/route_map.js",
]

# Workspace registered in fixtures for export
fixtures = [
    {"dt": "Report",     "filters": [["module", "=", "Logistics Transportation"]]},
    {"dt": "Workspace",  "filters": [["module", "=", "Logistics Transportation"]]},
    {"dt": "Notification", ...},
    "Logistics Settings",
]
```

### Git Commit History

| Commit | Description |
|---|---|
| `bfb266f` | feat: implement advanced logistics features (Vahan/Sarathi, Predictive Maintenance, NIC EWB, Google Maps, Driver Portal) |
| `2663ace` | feat: add advanced reports, automated notifications, and management workspace dashboard |
| `626b0ef` | fix: correct field name in Vehicle Profitability report |

---

## Summary — Before vs After

| Capability | Before | After |
|---|---|---|
| Government API Verification | ❌ Manual/None | ✅ Vahan RC + Sarathi DL with 1-click |
| Compliance Enforcement | ❌ None | ✅ Blocks trip dispatch if invalid |
| Predictive Maintenance | ❌ Manual only | ✅ Automated daily scheduler |
| E-Way Bill Generation | ❌ Manual portal | ✅ Direct NIC API from form |
| Route Visualization | ❌ None | ✅ Google Maps on all trip forms |
| Distance Calculation | ❌ Manual | ✅ Auto via Distance Matrix API |
| Real-time GPS Tracking | ❌ Text only | ✅ Pins plotted on live map |
| Driver Field Access | ❌ None | ✅ Mobile-first Driver Portal |
| Vehicle Profitability | ❌ No reports | ✅ Automated Script Report |
| Driver Performance | ❌ No reports | ✅ KPI Summary Report |
| Maintenance Alerts | ❌ Manual | ✅ Auto email + system notification |
| RC Expiry Alerts | ❌ None | ✅ Automated email |
| Management Dashboard | ❌ None | ✅ Dedicated Workspace |
