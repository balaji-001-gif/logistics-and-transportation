# Logistics & Transportation ERP 🚛💨

A high-performance, full-stack ERP solution for modern logistics and transportation companies in India. Built on the **Frappe / ERPNext v15** framework, this application streamlines everything from fleet compliance to customer billing.

---

## 🌟 Key Features

### 🏢 Fleet & Driver Compliance
*   **Vahan/Sarathi Integration**: Automated real-time verification of Vehicle RC and Driver DL status against government databases.
*   **Compliance Guard**: Intelligent blocks on Trip Dispatch if a vehicle's fitness or driver's license is expired.
*   **Document Management**: Centralized tracking for Insurance, Permits, and Pollution certificates.

### 🗺️ GPS Intelligence & Operations
*   **Interactive Maps**: Integrated Google Maps for route visualization on Freight Orders and Trip Sheets.
*   **Geocoding & Distance Matrix**: Automatic calculation of driving distances and transit times via Google APIs.
*   **Mobile Driver Portal**: A lightweight, mobile-first interface for drivers to update trip status (In Transit, Delivered) and log live fuel/toll expenses.

### 📦 Order & Load Management
*   **Freight Order**: End-to-end booking with automated GST (CGST/SGST/IGST) calculations.
*   **Load Planning**: Optimize fleet utilization by consolidating multiple orders into a single trip.
*   **Consignment Tracking**: Real-time tracking events plotted on interactive maps.

### 🧾 Finance & Compliance
*   **NIC E-Way Bill API**: Programmatic generation of E-Way Bills directly from the ERP, eliminating manual portal entry.
*   **3PL Billing**: Complex customer billing reconciliation and automated Freight Invoicing.
*   **Settlements**: Comprehensive trip-wise reconciliation of driver advances, fuel, and toll costs.

### 📊 Reports & Automation
*   **Predictive Maintenance**: Automated daily scheduler that creates maintenance requests based on odometer thresholds.
*   **Profitability Analysis**: Deep insights into Vehicle Profitability and Driver Trip performance.
*   **Global Logistics Settings**: A centralized configuration hub for all third-party API credentials.

---

## 🛠️ Technology Stack
*   **Backend**: Python (Frappe Framework v15)
*   **Frontend**: JavaScript (Vanilla JS), HTML5, CSS3
*   **Database**: MariaDB / PostgreSQL
*   **APIs**: Google Maps API, NIC E-Way Bill API, Vahan/Sarathi (via NIC Developer Portal)

---

## 🚀 Installation

```bash
# 1. Get the app
bench get-app https://github.com/balaji-001-gif/logistics-and-transportation.git

# 2. Install on your site
bench --site [your-site] install-app logistics_transport_erp

# 3. Build assets and migrate
bench build --app logistics_transport_erp
bench --site [your-site] migrate

# 4. Bootstrap Demo Data (Optional)
bench --site [your-site] execute logistics_transport_erp.demo_data.setup_all.run_all
```

---

## 📖 Documentation
Detailed Standard Operating Procedures (SOP) and User Manuals can be found in the [docs/SOP](docs/SOP) directory.

---
*Developed with ❤️ for the Logistics Industry.*
