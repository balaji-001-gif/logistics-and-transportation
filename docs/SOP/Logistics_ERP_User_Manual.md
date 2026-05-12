# Logistics & Transportation ERP: Standard Operating Procedure (SOP)

This document provides a step-by-step guide on how to operate the Logistics & Transportation ERP, from initial setup to final billing and settlement.

---

## 1. Master Data Setup (Foundation)
Before processing any orders, ensure your core assets and partners are registered in the system.

### 1.1 Fleet Management
*   **Vehicles**: Go to **Vehicle List** -> **New**. Enter the registration number, payload capacity, and fuel type. Attach RC, Insurance, and Fitness documents in the **Documents** child table to enable compliance tracking.
*   **Drivers**: Go to **Driver List** -> **New**. Link the driver to an Employee record and enter their DL (Driving License) details.

### 1.2 Logistics Network
*   **Route Master**: Define standard transit paths (e.g., Mumbai Hub to Delhi Gateway). Enter the estimated distance and transit time.
*   **Freight Rate Card**: Set up pricing for specific routes and customers. This ensures automated cost calculation in Freight Orders.

---

## 2. Commercial Setup
### 2.1 Customer Onboarding
*   **Customer**: Create the customer record in ERPNext.
*   **Customer Contract**: Link a Customer to a specific Service Level Agreement (SLA) and valid dates. This contract will be used to validate Freight Orders.

---

## 3. Order-to-Execution Workflow

### Step 1: Freight Order (Booking)
*   The lifecycle starts here. Create a **Freight Order** for a customer.
*   Select the **Route** and **Transport Mode**.
*   Add **Cargo Items** (Quantity, Weight, Volume).
*   The system will automatically calculate the freight charges based on the **Rate Card**.
*   **Submit** the Freight Order.

### Step 2: Load Planning
*   Go to **Load Plan**. This tool allows you to consolidate multiple Freight Orders into a single vehicle.
*   Select a **Vehicle** and **Driver**.
*   Add the Freight Orders that fit the vehicle's capacity.
*   **Submit** the Load Plan to trigger the creation of a **Trip Sheet**.

### Step 3: Trip Execution
*   The **Trip Sheet** is the operational heart of the journey.
*   **Departure**: Update the Start Odometer and Departure Time.
*   **Driver Portal**: The assigned driver logs into the `/driver-portal` on their mobile.
    *   They see their assigned trip.
    *   They click **"Update Status"** (In Transit, At Hub, etc.).
    *   The system captures their **GPS coordinates** and creates **Shipment Tracking Events**.

### Step 4: Tracking & Expenses
*   Managers can view real-time locations in the **Shipment Tracking Event** list or the map inside the Trip Sheet.
*   The driver can log **Fuel** and **Toll** expenses via the portal, which automatically populate the Trip Sheet.

---

## 4. Delivery & Proof (POD)
*   Upon reaching the destination, the driver or clerk creates a **POD (Proof of Delivery)**.
*   Attach a photo of the signed delivery note.
*   Status: **Delivered**. This updates the associated Freight Order status automatically.

---

## 5. Billing & Finance
### 5.1 Freight Invoice
*   Generate a **Freight Invoice** directly from the delivered Freight Order.
*   The system pulls the agreed rates and adds applicable **GST (CGST/SGST/IGST)**.
*   **Submit** the invoice to post it to the customer's ledger.

### 5.2 Freight Settlement
*   Finalize payments to vendors or owner-operators using the **Freight Settlement** DocType.
*   Reconcile against actual fuel and toll expenses captured during the trip.

---

## 6. Compliance & Reporting
*   **E-Way Bill**: Generate and track E-Way Bill expiry to avoid penalties.
*   **GST ITC Summary**: Run the query report to see tax breakdowns for all transport transactions.
*   **Trip Profitability**: Use the **Trip Profitability Report** to compare revenue vs. actual expenses (Fuel + Toll + Driver Advance).

---
*© 2026 BizAxl Logistics Solutions — Production Guide v1.0*
