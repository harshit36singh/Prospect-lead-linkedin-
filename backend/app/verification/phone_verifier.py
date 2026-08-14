from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import phonenumbers

PhoneStatus = Literal["valid", "invalid", "not_available"]


@dataclass(slots=True)
class PhoneVerificationResult:
    status: PhoneStatus
    is_possible: bool
    is_valid: bool
    formatted_e164: str | None
    detail: str


def verify_phone(raw_phone: str | None, default_region: str = "US") -> PhoneVerificationResult:
    if not raw_phone:
        return PhoneVerificationResult(
            status="not_available",
            is_possible=False,
            is_valid=False,
            formatted_e164=None,
            detail="No phone number provided",
        )

    try:
        parsed = phonenumbers.parse(raw_phone, default_region)
    except phonenumbers.NumberParseException as exc:
        return PhoneVerificationResult(
            status="invalid", is_possible=False, is_valid=False, formatted_e164=None, detail=str(exc)
        )

    is_possible = phonenumbers.is_possible_number(parsed)
    is_valid = phonenumbers.is_valid_number(parsed)

    if is_valid:
        formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        return PhoneVerificationResult(
            status="valid", is_possible=True, is_valid=True, formatted_e164=formatted, detail="Valid number"
        )

    return PhoneVerificationResult(
        status="invalid",
        is_possible=is_possible,
        is_valid=False,
        formatted_e164=None,
        detail="Not a valid number for its region",
    )
