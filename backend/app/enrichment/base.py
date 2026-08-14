from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.discovery.base import DiscoveredCompany, DiscoveredPerson


@dataclass(slots=True)
class EnrichmentResult:
    email: str | None
    email_confidence: float
    email_source: str | None
    phone: str | None
    phone_confidence: float


class EnrichmentProvider(ABC):
    @abstractmethod
    def enrich(self, person: DiscoveredPerson, company: DiscoveredCompany) -> EnrichmentResult: ...
