from __future__ import annotations

from app.discovery.base import DiscoverySource
from app.discovery.seed.source import SeedCompanySource

_SOURCES: dict[str, type[DiscoverySource]] = {
    "seed_companies": SeedCompanySource,
}


def get_discovery_source(name: str = "seed_companies") -> DiscoverySource:
    try:
        source_cls = _SOURCES[name]
    except KeyError as exc:
        raise ValueError(f"Unknown discovery source '{name}'") from exc
    return source_cls()
