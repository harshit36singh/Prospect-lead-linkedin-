from __future__ import annotations


def _norm(value: str) -> str:
    return value.strip().lower()


def industry_matches(company_industry: str, icp_industries: list[str]) -> bool:
    if not icp_industries:
        return True
    company_norm = _norm(company_industry)
    return any(_norm(i) in company_norm or company_norm in _norm(i) for i in icp_industries)


def size_overlaps(
    company_min: int | None,
    company_max: int | None,
    icp_min: int | None,
    icp_max: int | None,
) -> bool:
    if icp_min is None and icp_max is None:
        return True
    if company_min is None or company_max is None:
        return True
    lo = icp_min if icp_min is not None else company_min
    hi = icp_max if icp_max is not None else company_max
    return company_min <= hi and company_max >= lo


def size_near_miss(
    company_min: int | None,
    company_max: int | None,
    icp_min: int | None,
    icp_max: int | None,
    *,
    tolerance: float = 0.2,
) -> bool:
    """True if the ranges don't overlap but are within `tolerance` of doing so."""
    if company_min is None or company_max is None or (icp_min is None and icp_max is None):
        return False
    lo = icp_min if icp_min is not None else company_min
    hi = icp_max if icp_max is not None else company_max
    if company_min <= hi and company_max >= lo:
        return False  # already overlapping, not a "near miss"
    span = max(hi - lo, 1)
    gap = lo - company_max if company_max < lo else company_min - hi
    return 0 < gap <= span * tolerance


def location_matches(company_location: str, icp_locations: list[str]) -> bool:
    if not icp_locations:
        return True
    company_norm = _norm(company_location)
    return any(_norm(loc) in company_norm for loc in icp_locations)


def tech_overlap_ratio(company_technologies: list[str], icp_technologies: list[str]) -> float:
    if not icp_technologies:
        return 1.0
    company_norm = {_norm(t) for t in company_technologies}
    icp_norm = {_norm(t) for t in icp_technologies}
    if not icp_norm:
        return 1.0
    overlap = company_norm & icp_norm
    return len(overlap) / len(icp_norm)


def title_matches_any(title: str, target_titles: list[str]) -> bool:
    if not target_titles:
        return True
    title_norm = _norm(title)
    return any(_norm(t) in title_norm for t in target_titles)
