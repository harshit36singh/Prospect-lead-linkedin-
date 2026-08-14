from __future__ import annotations

import json
from pathlib import Path

from app.config import settings
from app.discovery.base import DiscoveredCompany, DiscoveredPerson, DiscoverySource
from app.discovery.github.client import GitHubClient
from app.matching import (
    industry_matches,
    location_matches,
    size_overlaps,
    tech_overlap_ratio,
    title_matches_any,
)
from app.schemas.icp import IcpRead

SOURCE_NAME = "seed_companies"


def _load_seed_companies(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


class SeedCompanySource(DiscoverySource):
    """Company discovery from a hand-curated list of real, publicly known
    companies (backend/data/seed_companies.json). This exists because there
    is no free, public, bulk company-search API equivalent to Reddit's RSS
    feeds -- so discovery starts from a real, user-extensible reference list
    instead of fabricated or ToS-gated data.
    """

    def __init__(self, seed_path: Path | None = None, github_client: GitHubClient | None = None):
        self._seed_path = seed_path or settings.seed_companies_path
        self._github = github_client or GitHubClient()

    def _all_companies(self) -> list[DiscoveredCompany]:
        raw = _load_seed_companies(self._seed_path)
        return [
            DiscoveredCompany(
                source=SOURCE_NAME,
                source_ref=item["domain"],
                name=item["name"],
                domain=item["domain"],
                industry=item["industry"],
                size_label=item["size_label"],
                size_min=item.get("size_min"),
                size_max=item.get("size_max"),
                location=item["location"],
                technologies=item.get("technologies", []),
                github_org=item.get("github_org"),
            )
            for item in raw
        ]

    def search_companies(self, icp: IcpRead) -> list[DiscoveredCompany]:
        matches = []
        for company in self._all_companies():
            if not industry_matches(company.industry, icp.industries):
                continue
            if not size_overlaps(
                company.size_min, company.size_max, icp.company_size_min, icp.company_size_max
            ):
                continue
            if not location_matches(company.location, icp.locations):
                continue
            if icp.technologies and tech_overlap_ratio(company.technologies, icp.technologies) <= 0:
                continue
            matches.append(company)
        return matches

    def find_people(self, company: DiscoveredCompany, icp: IcpRead) -> list[DiscoveredPerson]:
        if not company.github_org:
            return []
        members = self._github.list_public_members_with_titles(company.github_org)
        people = [
            DiscoveredPerson(
                source="github_public_api",
                source_ref=f"{company.github_org}/{login}",
                full_name=name,
                title=title,
                location=location or company.location,
                company_source_ref=company.source_ref,
            )
            for login, name, title, location in members
            if name and title
        ]
        if icp.target_titles:
            people = [p for p in people if title_matches_any(p.title, icp.target_titles)]
        return people
