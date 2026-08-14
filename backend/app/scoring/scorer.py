from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

from rapidfuzz import fuzz

from app.matching import industry_matches, location_matches, size_near_miss, size_overlaps, tech_overlap_ratio
from app.models.company import Company, Contact
from app.models.icp import Icp

Grade = Literal["Hot", "Warm", "Cold"]

INDUSTRY_MATCH_POINTS = 25
SIZE_FIT_POINTS = 15
SIZE_NEAR_MISS_POINTS = 7
LOCATION_MATCH_POINTS = 15
TECH_OVERLAP_MAX_POINTS = 20
TITLE_STRONG_MATCH_POINTS = 15
TITLE_WEAK_MATCH_POINTS = 7
TITLE_STRONG_THRESHOLD = 80
TITLE_WEAK_THRESHOLD = 60
EMAIL_VALID_POINTS = 8
EMAIL_INVALID_POINTS = -5
PHONE_VALID_POINTS = 2

HOT_THRESHOLD = 75
WARM_THRESHOLD = 45


@dataclass(slots=True)
class ScoreBreakdown:
    industry_match: int
    size_fit: int
    location_fit: int
    tech_overlap: int
    title_match: int
    email_adjustment: int
    phone_adjustment: int
    total: int
    grade: Grade

    def as_dict(self) -> dict:
        return asdict(self)


def _title_score(contact_title: str, target_titles: list[str]) -> int:
    if not target_titles or not contact_title:
        return 0
    best = max(fuzz.ratio(contact_title.lower(), t.lower()) for t in target_titles)
    if best >= TITLE_STRONG_THRESHOLD:
        return TITLE_STRONG_MATCH_POINTS
    if best >= TITLE_WEAK_THRESHOLD:
        return TITLE_WEAK_MATCH_POINTS
    return 0


def _grade(total: int) -> Grade:
    if total >= HOT_THRESHOLD:
        return "Hot"
    if total >= WARM_THRESHOLD:
        return "Warm"
    return "Cold"


def score_lead(company: Company, contact: Contact, icp: Icp) -> ScoreBreakdown:
    industry_pts = INDUSTRY_MATCH_POINTS if industry_matches(company.industry, icp.industries) else 0

    if size_overlaps(company.size_min, company.size_max, icp.company_size_min, icp.company_size_max):
        size_pts = SIZE_FIT_POINTS
    elif size_near_miss(
        company.size_min, company.size_max, icp.company_size_min, icp.company_size_max
    ):
        size_pts = SIZE_NEAR_MISS_POINTS
    else:
        size_pts = 0

    location_pts = LOCATION_MATCH_POINTS if location_matches(company.location, icp.locations) else 0

    tech_pts = (
        round(TECH_OVERLAP_MAX_POINTS * tech_overlap_ratio(company.technologies, icp.technologies))
        if icp.technologies
        else 0
    )

    title_pts = _title_score(contact.title, icp.target_titles)

    email_pts = 0
    if contact.email_verification_status == "valid":
        email_pts = EMAIL_VALID_POINTS
    elif contact.email_verification_status == "invalid":
        email_pts = EMAIL_INVALID_POINTS

    phone_pts = PHONE_VALID_POINTS if contact.phone_verification_status == "valid" else 0

    raw_total = (
        industry_pts + size_pts + location_pts + tech_pts + title_pts + email_pts + phone_pts
    )
    total = max(0, min(100, raw_total))

    return ScoreBreakdown(
        industry_match=industry_pts,
        size_fit=size_pts,
        location_fit=location_pts,
        tech_overlap=tech_pts,
        title_match=title_pts,
        email_adjustment=email_pts,
        phone_adjustment=phone_pts,
        total=total,
        grade=_grade(total),
    )
