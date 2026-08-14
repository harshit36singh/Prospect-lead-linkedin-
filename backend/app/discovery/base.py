from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.schemas.icp import IcpRead


@dataclass(slots=True)
class DiscoveredCompany:
    source: str
    source_ref: str
    name: str
    domain: str
    industry: str
    size_label: str
    size_min: int | None
    size_max: int | None
    location: str
    technologies: list[str] = field(default_factory=list)
    github_org: str | None = None


@dataclass(slots=True)
class DiscoveredPerson:
    source: str
    source_ref: str
    full_name: str
    title: str
    location: str
    company_source_ref: str


class DiscoverySource(ABC):
    """A pluggable source of companies and decision-makers.

    Implementations must only use data that is genuinely public and either
    intended for programmatic access (a published API/feed) or curated by a
    human (a seed list) -- never automation against a login-gated platform.
    """

    @abstractmethod
    def search_companies(self, icp: IcpRead) -> list[DiscoveredCompany]: ...

    @abstractmethod
    def find_people(self, company: DiscoveredCompany, icp: IcpRead) -> list[DiscoveredPerson]: ...
