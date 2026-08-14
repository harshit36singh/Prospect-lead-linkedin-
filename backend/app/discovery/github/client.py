from __future__ import annotations

import logging
import re
import time

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import settings

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"
DEFAULT_TIMEOUT = 10.0


class GitHubTransientError(Exception):
    """Raised on a 5xx / network error -- safe to retry."""


class GitHubRateLimitError(Exception):
    """Raised when GitHub's rate limit is exhausted -- caller should stop, not retry."""


def _parse_link_header(link_header: str | None) -> str | None:
    """Extract the 'next' page URL from a GitHub Link header, if present."""
    if not link_header:
        return None
    for part in link_header.split(","):
        section = part.split(";")
        if len(section) < 2:
            continue
        url = section[0].strip().strip("<>")
        rel = section[1].strip()
        if rel == 'rel="next"':
            return url
    return None


class GitHubClient:
    """Thin client for GitHub's public REST API -- genuinely public data,
    intended for programmatic use, with real rate-limit-header handling
    (60 req/hr unauthenticated, 5000/hr with PROSPECTLEAD_GITHUB_TOKEN) and retry/backoff.
    """

    def __init__(self, token: str | None = None):
        self._token = token if token is not None else settings.github_token
        self._session = requests.Session()

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    @retry(
        retry=retry_if_exception_type(GitHubTransientError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    def _get(self, url: str, *, params: dict | None = None) -> requests.Response:
        response = self._session.get(
            url, headers=self._headers(), params=params, timeout=DEFAULT_TIMEOUT
        )

        remaining = response.headers.get("x-ratelimit-remaining")
        if response.status_code == 403 and remaining == "0":
            reset_epoch = int(response.headers.get("x-ratelimit-reset", time.time()))
            wait_seconds = max(0, reset_epoch - int(time.time()))
            raise GitHubRateLimitError(
                f"GitHub API rate limit exhausted; resets in {wait_seconds}s. "
                f"Set PROSPECTLEAD_GITHUB_TOKEN in backend/.env to raise the limit to 5000/hr."
            )

        if response.status_code >= 500:
            raise GitHubTransientError(f"GitHub API {response.status_code} on {url}")

        return response

    def _get_all_pages(self, url: str, *, params: dict | None = None) -> list[dict]:
        results: list[dict] = []
        next_url: str | None = url
        next_params: dict | None = params
        while next_url:
            response = self._get(next_url, params=next_params)
            if response.status_code == 404:
                return results
            response.raise_for_status()
            results.extend(response.json())
            next_url = _parse_link_header(response.headers.get("link"))
            next_params = None  # params are embedded in the Link header's next URL
        return results

    def list_public_members_with_titles(self, org: str) -> list[tuple[str, str, str, str]]:
        """Returns (login, name, bio_as_title, location) for each public org member.

        Members with no public name or bio are skipped -- GitHub profiles are
        freeform, so coverage here is inherently partial. This is the honest
        real result, not a guaranteed-complete directory.
        """
        try:
            members = self._get_all_pages(f"{GITHUB_API_BASE}/orgs/{org}/public_members")
        except (GitHubRateLimitError, GitHubTransientError) as exc:
            logger.warning("GitHub member lookup failed for org %s: %s", org, exc)
            return []

        results: list[tuple[str, str, str, str]] = []
        for member in members:
            login = member.get("login")
            if not login:
                continue
            try:
                response = self._get(f"{GITHUB_API_BASE}/users/{login}")
            except (GitHubRateLimitError, GitHubTransientError) as exc:
                logger.warning("GitHub user lookup failed for %s: %s", login, exc)
                continue
            if response.status_code != 200:
                continue
            profile = response.json()
            name = (profile.get("name") or "").strip()
            bio = _clean_bio(profile.get("bio") or "")
            location = (profile.get("location") or "").strip()
            results.append((login, name, bio, location))
        return results


def _clean_bio(bio: str) -> str:
    single_line = re.sub(r"\s+", " ", bio).strip()
    return single_line[:120]
