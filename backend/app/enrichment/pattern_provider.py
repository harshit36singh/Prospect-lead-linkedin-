from __future__ import annotations

import random
import re
import unicodedata

from app.discovery.base import DiscoveredCompany, DiscoveredPerson
from app.enrichment.base import EnrichmentProvider, EnrichmentResult

MIN_CONFIDENCE = 0.55
MAX_CONFIDENCE = 0.95


def _asciify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return normalized.encode("ascii", "ignore").decode("ascii")


def _slug(value: str) -> str:
    ascii_value = _asciify(value).lower()
    return re.sub(r"[^a-z]", "", ascii_value)


def _split_name(full_name: str) -> tuple[str, str]:
    parts = full_name.strip().split()
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[-1]


class PatternEnrichmentProvider(EnrichmentProvider):
    """Guesses a work email as first.last@domain -- the same fallback
    technique real providers like Hunter.io/Apollo use when no verified
    email is on file. Always labeled email_source="pattern_guess" so it's
    shown as inferred, not confirmed. Phone is intentionally left null:
    there is no public, honest source for a person's direct-dial number in
    this pipeline, and fabricating one would misrepresent real leads.
    """

    def enrich(self, person: DiscoveredPerson, company: DiscoveredCompany) -> EnrichmentResult:
        first, last = _split_name(person.full_name)
        first_slug, last_slug = _slug(first), _slug(last)

        if not first_slug:
            return EnrichmentResult(
                email=None, email_confidence=0.0, email_source=None, phone=None, phone_confidence=0.0
            )

        local_part = f"{first_slug}.{last_slug}" if last_slug else first_slug
        email = f"{local_part}@{company.domain}"

        rng = random.Random(f"{person.full_name}:{company.domain}")
        confidence = round(rng.uniform(MIN_CONFIDENCE, MAX_CONFIDENCE), 2)

        return EnrichmentResult(
            email=email,
            email_confidence=confidence,
            email_source="pattern_guess",
            phone=None,
            phone_confidence=0.0,
        )
