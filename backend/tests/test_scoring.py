from __future__ import annotations

from types import SimpleNamespace

from app.scoring.scorer import score_lead


def make_icp(**overrides):
    defaults = dict(
        industries=[],
        company_size_min=None,
        company_size_max=None,
        locations=[],
        technologies=[],
        target_titles=[],
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def make_company(**overrides):
    defaults = dict(industry="", size_min=None, size_max=None, location="", technologies=[])
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def make_contact(**overrides):
    defaults = dict(title="", email_verification_status="unverified", phone_verification_status="not_available")
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def test_perfect_match_scores_100_and_hot():
    icp = make_icp(
        industries=["Developer Tools"],
        company_size_min=200,
        company_size_max=2000,
        locations=["USA"],
        technologies=["Kubernetes", "Go"],
        target_titles=["VP Engineering"],
    )
    company = make_company(
        industry="Developer Tools",
        size_min=300,
        size_max=500,
        location="Palo Alto, USA",
        technologies=["Go", "Docker", "Kubernetes"],
    )
    contact = make_contact(
        title="VP of Engineering",
        email_verification_status="valid",
        phone_verification_status="valid",
    )

    breakdown = score_lead(company, contact, icp)

    assert breakdown.industry_match == 25
    assert breakdown.size_fit == 15
    assert breakdown.location_fit == 15
    assert breakdown.tech_overlap == 20
    assert breakdown.title_match == 15
    assert breakdown.email_adjustment == 8
    assert breakdown.phone_adjustment == 2
    assert breakdown.total == 100
    assert breakdown.grade == "Hot"


def test_no_match_scores_zero_and_cold():
    icp = make_icp(
        industries=["Fintech"],
        company_size_min=1000,
        company_size_max=1200,
        locations=["Germany"],
        technologies=["Rust"],
        target_titles=["CFO"],
    )
    company = make_company(
        industry="Developer Tools", size_min=300, size_max=500, location="Palo Alto, USA", technologies=["Go"]
    )
    contact = make_contact(title="Intern", email_verification_status="invalid")

    breakdown = score_lead(company, contact, icp)

    assert breakdown.total == 0  # clipped from a negative raw total
    assert breakdown.grade == "Cold"


def test_size_near_miss_awards_partial_credit():
    icp = make_icp(company_size_min=550, company_size_max=1000)
    company = make_company(size_min=300, size_max=500)  # gap of 50, within 20% tolerance of 450 span
    contact = make_contact()

    breakdown = score_lead(company, contact, icp)

    assert breakdown.size_fit == 7


def test_empty_icp_technologies_does_not_award_tech_points():
    icp = make_icp(technologies=[])
    company = make_company(technologies=["Go", "Kubernetes"])
    contact = make_contact()

    breakdown = score_lead(company, contact, icp)

    assert breakdown.tech_overlap == 0


def test_below_warm_threshold_grades_cold():
    # Industry + location match (40 pts), but company size is wildly outside
    # the ICP range and not a near-miss, so size contributes 0 -- total stays
    # just below the 45-point Warm threshold.
    icp = make_icp(industries=["X"], locations=["Y"], company_size_min=1000, company_size_max=2000)
    company = make_company(industry="X", location="Y", size_min=1, size_max=10)
    contact = make_contact()

    breakdown = score_lead(company, contact, icp)

    assert breakdown.total == 40
    assert breakdown.grade == "Cold"
