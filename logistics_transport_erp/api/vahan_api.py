"""
Vahan / Sarathi API Integration
================================
Wraps the NIC VAHAN (vehicle RC) and Sarathi (driver DL) REST APIs.

Docs / Registration:
  - Vahan:   https://vahan.parivahan.gov.in/vahanservice
  - Sarathi:  https://sarathi.parivahan.gov.in/sarathiservice

When `vahan_api_enabled` is False in Logistics Settings the functions
return a graceful "API disabled" dict instead of raising an error —
useful for development without real credentials.
"""

import frappe
import requests


_VAHAN_BASE_SANDBOX = "https://apisetu.gov.in/vahan/v3"
_VAHAN_BASE_PROD    = "https://apisetu.gov.in/vahan/v3"  # same endpoint; swap for official prod URL when known

_SARATHI_BASE        = "https://apisetu.gov.in/sarathi/v3"


def _settings():
    return frappe.get_single("Logistics Settings")


def _api_disabled_response(entity: str) -> dict:
    return {
        "status": "API Disabled",
        "message": f"Enable 'Vahan/Sarathi Validation' in Logistics Settings to verify {entity}.",
        "verified": False,
    }


# ─────────────────────────────────────────────
# Vehicle RC (Registration Certificate)
# ─────────────────────────────────────────────

def check_rc_status(registration_number: str) -> dict:
    """
    Query Vahan API for a vehicle's RC status.

    Returns a dict with keys:
        verified        bool
        rc_status       str  e.g. "Active", "Blacklisted", "Scrapped"
        fitness_upto    str  ISO date or ""
        owner_name      str
        message         str  human-readable summary
    """
    s = _settings()
    if not s.vahan_api_enabled:
        return _api_disabled_response("Vehicle RC")

    api_key = s.get_password("vahan_api_key") or ""
    if not api_key:
        frappe.throw(frappe._("Vahan API Key not configured in Logistics Settings."))

    reg_no = (registration_number or "").replace(" ", "").upper()

    try:
        resp = requests.get(
            f"{_VAHAN_BASE_SANDBOX}/rc/findByRegNo",
            params={"regNo": reg_no, "state": "0"},
            headers={
                "X-Api-Key": api_key,
                "Accept":    "application/json",
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.Timeout:
        frappe.log_error("Vahan API timeout", "Vahan RC Check")
        return {"verified": False, "rc_status": "Error", "message": "Vahan API timed out. Please retry."}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Vahan RC Check")
        return {"verified": False, "rc_status": "Error", "message": str(e)}

    # Normalise response (sandbox schema)
    vehicle_data = data.get("result", data)  # sandbox wraps in "result"
    rc_status  = vehicle_data.get("rcStatus", vehicle_data.get("status", "Unknown"))
    fitness    = vehicle_data.get("fitnessupto", vehicle_data.get("fitnessUpto", ""))
    owner      = vehicle_data.get("ownerName", "")

    return {
        "verified":     True,
        "rc_status":    rc_status,
        "fitness_upto": fitness,
        "owner_name":   owner,
        "message":      f"RC Status: {rc_status} | Fitness Upto: {fitness or 'N/A'} | Owner: {owner}",
    }


# ─────────────────────────────────────────────
# Driver Licence (DL)
# ─────────────────────────────────────────────

def check_dl_status(dl_number: str, date_of_birth: str) -> dict:
    """
    Query Sarathi API for a driver licence status.

    Args:
        dl_number   e.g. "MH0120210012345"
        date_of_birth  ISO date string "YYYY-MM-DD"

    Returns a dict with keys:
        verified        bool
        dl_status       str  e.g. "Active", "Expired", "Suspended"
        valid_upto      str  ISO date or ""
        dl_class        str  e.g. "HMV, LMV"
        message         str
    """
    s = _settings()
    if not s.vahan_api_enabled:
        return _api_disabled_response("Driver Licence")

    api_key = s.get_password("vahan_api_key") or ""
    if not api_key:
        frappe.throw(frappe._("Vahan API Key not configured in Logistics Settings."))

    dob_str = (date_of_birth or "").replace("-", "")  # API expects DDMMYYYY sometimes
    if len(dob_str) == 8:
        # Convert YYYYMMDD -> DDMMYYYY
        dob_str = dob_str[6:8] + dob_str[4:6] + dob_str[0:4]

    try:
        resp = requests.post(
            f"{_SARATHI_BASE}/dl/getDrivingLicenseDetail",
            json={"dlNo": dl_number.upper(), "dob": dob_str},
            headers={
                "X-Api-Key":    api_key,
                "Content-Type": "application/json",
                "Accept":       "application/json",
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.Timeout:
        frappe.log_error("Sarathi API timeout", "Sarathi DL Check")
        return {"verified": False, "dl_status": "Error", "message": "Sarathi API timed out. Please retry."}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Sarathi DL Check")
        return {"verified": False, "dl_status": "Error", "message": str(e)}

    dl_data   = data.get("result", data)
    dl_status = dl_data.get("dlStatus", dl_data.get("status", "Unknown"))
    valid_to  = dl_data.get("validUpto", dl_data.get("expiryDate", ""))
    dl_class  = dl_data.get("vehicleClass", dl_data.get("dlClass", ""))

    return {
        "verified":  True,
        "dl_status": dl_status,
        "valid_upto": valid_to,
        "dl_class":  dl_class,
        "message":   f"DL Status: {dl_status} | Valid Upto: {valid_to or 'N/A'} | Class: {dl_class}",
    }
