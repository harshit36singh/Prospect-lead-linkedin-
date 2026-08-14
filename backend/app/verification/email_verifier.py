from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

import dns.exception
import dns.resolver

EMAIL_FORMAT_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

EmailStatus = Literal["valid", "invalid", "risky", "unverifiable"]


@dataclass(slots=True)
class EmailVerificationResult:
    status: EmailStatus
    is_valid_format: bool
    has_mx_record: bool
    detail: str


def verify_email(email: str | None, *, timeout: float = 3.0) -> EmailVerificationResult:
    if not email:
        return EmailVerificationResult(
            status="unverifiable", is_valid_format=False, has_mx_record=False, detail="No email provided"
        )

    if not EMAIL_FORMAT_RE.match(email):
        return EmailVerificationResult(
            status="invalid", is_valid_format=False, has_mx_record=False, detail="Malformed email address"
        )

    domain = email.rsplit("@", 1)[-1]
    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=timeout)
        has_mx = len(answers) > 0
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return EmailVerificationResult(
            status="invalid",
            is_valid_format=True,
            has_mx_record=False,
            detail=f"Domain {domain} has no MX record",
        )
    except (dns.exception.DNSException, OSError) as exc:
        return EmailVerificationResult(
            status="unverifiable",
            is_valid_format=True,
            has_mx_record=False,
            detail=f"DNS lookup failed: {exc}",
        )

    if has_mx:
        return EmailVerificationResult(
            status="valid", is_valid_format=True, has_mx_record=True, detail=f"{domain} accepts mail"
        )
    return EmailVerificationResult(
        status="invalid", is_valid_format=True, has_mx_record=False, detail=f"{domain} has no MX record"
    )
