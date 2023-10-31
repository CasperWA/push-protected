"""Validate inputs."""
from __future__ import annotations

from urllib.parse import urlsplit


VALID_CONCLUSIONS = [
    "action_required",
    "cancelled",
    "failure",
    "neutral",
    "skipped",
    "success",
    "timed_out",
]
"""List of valid GitHub Actions workflow job run conclusions.
This is taken from
https://docs.github.com/en/rest/actions/workflow-jobs?apiVersion=2022-11-28#get-a-job-for-a-workflow-run
as of 30.10.2023.
"""

GITHUB_FREE_REST_API_BASE_URL = "https://api.github.com"
"""Base URL for GitHub Free API."""

GITHUB_ENTERPRISE_API_PREFIX = "/api/v3"
"""Prefix for GitHub Enterprise API URLs.
See the note for more information here:
https://docs.github.com/en/enterprise-server@3.10/rest/quickstart?apiVersion=2022-11-28&tool=curl#using-curl-commands-in-github-actions.
"""


def validate_conclusions(conclusions: list[str]) -> list[str]:
    """Validate the conclusions.

    I.e., ensure they are valid GitHub Actions workflow job run conclusions.
    """
    if not conclusions:
        raise ValueError(
            "No conclusions supplied - at least one is required (default: 'success')."
        )

    # Remove redundant entries and conform to lowercase
    conclusions = list(set(conclusion.lower() for conclusion in conclusions))

    for conclusion in conclusions:
        invalid_conclusions: list[str] = []
        if conclusion not in VALID_CONCLUSIONS:
            invalid_conclusions.append(conclusion)

    if invalid_conclusions:
        return [
            f"Invalid supplied conclusions: {invalid_conclusions}. "
            f"Valid conclusions are: {VALID_CONCLUSIONS}"
        ]

    return conclusions


def validate_rest_api_base_url(base_url: str) -> str:
    """Validate and parse the `gh_rest_api_base_url` input."""
    split_base_url = urlsplit(base_url)

    if not split_base_url.scheme or not split_base_url.netloc:
        raise ValueError(
            "Invalid URL provided for `gh_rest_api_base_url` input (missing scheme "
            "and/or netloc)."
        )

    compiled_url = split_base_url.scheme + "://" + split_base_url.netloc

    if compiled_url == GITHUB_FREE_REST_API_BASE_URL:
        return compiled_url

    url_path = split_base_url.path.rstrip("/")

    if url_path and not split_base_url.path.endswith(GITHUB_ENTERPRISE_API_PREFIX):
        raise ValueError(
            "Invalid URL provided for `gh_rest_api_base_url` input (path must end with "
            f"{GITHUB_ENTERPRISE_API_PREFIX!r})."
        )

    if not url_path:
        compiled_url += GITHUB_ENTERPRISE_API_PREFIX

    return compiled_url
