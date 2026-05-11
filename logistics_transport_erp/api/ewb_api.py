"""
NIC E-Way Bill (EWB) API Integration
======================================
Handles authentication and EWB creation via the GST/NIC portal.

API Sandbox: https://einvoice1-sandbox.nic.in/EWB
Production:  https://einvapi.nic.in/EWB   (requires NIC approval)

Auth token is cached in Frappe's cache for 6 hours (NIC token TTL).

Reference:
  https://einvoice1.gst.gov.in/Others/SandboxDoc
"""

import frappe
import requests
from frappe import _
from frappe.utils import now_datetime

_SANDBOX_BASE = "https://einvoice1-sandbox.nic.in/EWB/ewbapi"
_PROD_BASE    = "https://einvapi.nic.in/EWB/ewbapi"

_CACHE_KEY = "nic_ewb_auth_token"


def _settings():
    return frappe.get_single("Logistics Settings")


def _base_url(settings) -> str:
    return _PROD_BASE if settings.nic_api_environment == "Production" else _SANDBOX_BASE


def _get_headers(settings) -> dict:
    token = _get_auth_token(settings)
    return {
        "authtoken":    token,
        "Gstin":        settings.nic_gstin or "",
        "Content-Type": "application/json",
        "Accept":       "application/json",
    }


# ─────────────────────────────────────────────
# Authentication
# ─────────────────────────────────────────────

def _get_auth_token(settings) -> str:
    """
    Returns a valid NIC auth token, refreshing from cache or re-authenticating as needed.
    Token is cached for 5.5 hours (NIC TTL is 6 hours).
    """
    cached = frappe.cache().get_value(_CACHE_KEY)
    if cached:
        return cached

    username = settings.nic_username or ""
    password = settings.get_password("nic_password") or ""
    gstin    = settings.nic_gstin or ""

    if not (username and password and gstin):
        frappe.throw(_("NIC credentials (GSTIN, Username, Password) are not configured in Logistics Settings."))

    try:
        resp = requests.post(
            f"{_base_url(settings)}/user/auth",
            json={
                "action":   "ACCESSTOKEN",
                "username": username,
                "password": password,
                "gstin":    gstin,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data  = resp.json()
    except requests.exceptions.Timeout:
        frappe.throw(_("NIC API timed out during authentication. Please retry."))
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "NIC EWB Auth")
        frappe.throw(_("NIC Authentication failed: {0}").format(str(e)))

    if data.get("status") != "1":
        frappe.throw(_("NIC Auth Error: {0}").format(data.get("error", "Unknown error")))

    token = data.get("authtoken") or data.get("data", {}).get("authtoken", "")
    frappe.cache().set_value(_CACHE_KEY, token, expires_in_sec=19800)  # 5.5 hours
    return token


def invalidate_token():
    """Call this when auth fails mid-session to force re-login."""
    frappe.cache().delete_value(_CACHE_KEY)


# ─────────────────────────────────────────────
# EWB Generation
# ─────────────────────────────────────────────

def generate_ewb(ewb_doc) -> dict:
    """
    Generate an E-Way Bill for a given EWB document.

    Args:
        ewb_doc: Frappe Document object of type "E Way Bill"

    Returns:
        dict with keys: ewb_number, valid_upto, ewb_date, raw_response
    """
    settings = _settings()

    # Build payload from document fields
    payload = _build_ewb_payload(ewb_doc, settings)

    try:
        resp = requests.post(
            f"{_base_url(settings)}/ewayapi/genewaybill",
            json=payload,
            headers=_get_headers(settings),
            timeout=20,
        )

        # NIC returns 401 when token expired — refresh and retry once
        if resp.status_code == 401:
            invalidate_token()
            resp = requests.post(
                f"{_base_url(settings)}/ewayapi/genewaybill",
                json=payload,
                headers=_get_headers(settings),
                timeout=20,
            )

        resp.raise_for_status()
        data = resp.json()

    except requests.exceptions.Timeout:
        frappe.throw(_("NIC EWB API timed out. Please retry."))
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "NIC EWB Generation")
        frappe.throw(_("EWB Generation failed: {0}").format(str(e)))

    if str(data.get("status")) != "1":
        error_msg = data.get("error", {})
        if isinstance(error_msg, dict):
            error_msg = error_msg.get("message", str(error_msg))
        frappe.throw(_("NIC EWB Error: {0}").format(error_msg))

    result_data = data.get("data", data)
    return {
        "ewb_number":    str(result_data.get("ewbNo", result_data.get("ewayBillNo", ""))),
        "valid_upto":    result_data.get("validUpto", result_data.get("ewbValidTill", "")),
        "ewb_date":      result_data.get("ewbDt",    str(now_datetime())),
        "raw_response":  data,
    }


def _build_ewb_payload(ewb_doc, settings) -> dict:
    """Maps EWB DocType fields to NIC API payload."""
    return {
        "action":        "GENEWAYBILL",
        "version":       "1.0.1",
        "billDate":      str(ewb_doc.generated_date or ""),
        "billNumber":    ewb_doc.name,
        "fromGstin":     settings.nic_gstin or "",
        "fromTrdName":   frappe.db.get_single_value("Global Defaults", "default_company") or "",
        "fromAddr1":     "",
        "fromPlace":     ewb_doc.get("origin_place", ""),
        "fromPincode":   int(ewb_doc.get("origin_pincode", 0) or 0),
        "fromStateCode": int(ewb_doc.get("origin_state_code", 0) or 0),
        "actFromStateCode": int(ewb_doc.get("origin_state_code", 0) or 0),
        "toGstin":       ewb_doc.get("consignee_gstin", "URP"),
        "toTrdName":     ewb_doc.get("consignee_name", ""),
        "toAddr1":       ewb_doc.get("consignee_address", ""),
        "toPlace":       ewb_doc.get("destination_place", ""),
        "toPincode":     int(ewb_doc.get("destination_pincode", 0) or 0),
        "toStateCode":   int(ewb_doc.get("destination_state_code", 0) or 0),
        "actToStateCode": int(ewb_doc.get("destination_state_code", 0) or 0),
        "transactionType": 1,
        "otherValue":    0,
        "totalValue":    float(ewb_doc.get("invoice_value", 0) or 0),
        "cgstValue":     float(ewb_doc.get("cgst_amount", 0)   or 0),
        "sgstValue":     float(ewb_doc.get("sgst_amount", 0)   or 0),
        "igstValue":     float(ewb_doc.get("igst_amount", 0)   or 0),
        "cessValue":     0,
        "transporterId": "",
        "transporterName": ewb_doc.get("transporter_name", ""),
        "transDocNo":    ewb_doc.get("lr_number", ewb_doc.name),
        "transDocDate":  str(ewb_doc.get("lr_date", ewb_doc.generated_date) or ""),
        "transMode":     ewb_doc.get("transport_mode", "1"),
        "vehicleNo":     ewb_doc.get("vehicle_number", ""),
        "vehicleType":   "R",
        "itemList": [
            {
                "productName":  ewb_doc.get("goods_description", "Goods"),
                "productDesc":  ewb_doc.get("goods_description", "Goods"),
                "hsnCode":      str(ewb_doc.get("hsn_code", "9965")),
                "quantity":     float(ewb_doc.get("quantity", 1) or 1),
                "qtyUnit":      ewb_doc.get("unit", "NOS"),
                "cgstRate":     float(ewb_doc.get("cgst_rate", 0) or 0),
                "sgstRate":     float(ewb_doc.get("sgst_rate", 0) or 0),
                "igstRate":     float(ewb_doc.get("igst_rate", 0) or 0),
                "cessRate":     0,
                "taxableAmount": float(ewb_doc.get("invoice_value", 0) or 0),
            }
        ],
    }
