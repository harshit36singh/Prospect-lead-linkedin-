from __future__ import annotations

from pathlib import Path

import gspread

from app.config import settings
from app.models.lead import Lead

HEADER_ROW = [
    "Score",
    "Grade",
    "Company",
    "Domain",
    "Industry",
    "Contact",
    "Title",
    "Email",
    "Email Source",
    "Email Status",
    "Phone",
    "Phone Status",
]


class SheetsExportError(Exception):
    pass


def _lead_row(lead: Lead) -> list:
    return [
        lead.score,
        lead.grade,
        lead.company.name,
        lead.company.domain,
        lead.company.industry,
        lead.contact.full_name,
        lead.contact.title,
        lead.contact.email or "",
        lead.contact.email_source or "",
        lead.contact.email_verification_status,
        lead.contact.phone or "",
        lead.contact.phone_verification_status,
    ]


def export_leads_to_sheet(leads: list[Lead], sheet_name: str) -> str:
    """Writes leads to a Google Sheet (creating it if needed) and returns its URL.

    Raises SheetsExportError with an actionable message if
    GOOGLE_SERVICE_ACCOUNT_JSON isn't configured -- this is the one
    integration point the user must set up by hand (a Google Cloud service
    account with Sheets API access, shared with the target spreadsheet).
    """
    if not settings.google_service_account_json:
        raise SheetsExportError(
            "Google Sheets export isn't configured. Set GOOGLE_SERVICE_ACCOUNT_JSON "
            "in backend/.env to the path of a Google service-account JSON key "
            "(create one at https://console.cloud.google.com, enable the Sheets API, "
            "and share your target spreadsheet with the service account's client_email)."
        )

    credential_path = Path(settings.google_service_account_json)
    if not credential_path.exists():
        raise SheetsExportError(
            f"GOOGLE_SERVICE_ACCOUNT_JSON points to {credential_path}, which doesn't exist."
        )

    try:
        gc = gspread.service_account(filename=str(credential_path))
    except Exception as exc:  # noqa: BLE001
        raise SheetsExportError(f"Failed to authenticate with Google: {exc}") from exc

    try:
        spreadsheet = gc.open(sheet_name)
    except gspread.SpreadsheetNotFound:
        try:
            spreadsheet = gc.create(sheet_name)
        except Exception as exc:  # noqa: BLE001
            raise SheetsExportError(f"Failed to create spreadsheet '{sheet_name}': {exc}") from exc

    worksheet = spreadsheet.sheet1
    worksheet.clear()
    rows = [HEADER_ROW] + [_lead_row(lead) for lead in leads]
    worksheet.update(rows)

    return spreadsheet.url
