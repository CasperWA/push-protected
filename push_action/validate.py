"""Validate inputs."""
from __future__ import annotations


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


def validate_conclusions(conclusions: list[str]) -> list[str]:
    """Validate the conclusions.

    I.e., ensure they are valid GitHub Actions workflow job run conclusions.
    """
    if not conclusions:
        raise ValueError(
            "No conclusions supplied - at least one is required (default: 'success')."
        )

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
