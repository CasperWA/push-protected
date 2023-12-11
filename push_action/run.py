"""push_action.run

This is the main module implementing the CLI `push-action`.

The steps of progression for the whole of the action are the following:

1) Get required statuses for branch (GitHub Actions jobs / third party status checks)
   from:
   {input_gh_rest_api_base_url}/repos/:owner/:repo/branches/:branch
   protection -> required_status_checks -> contexts

2) Get GitHub Actions runs for specific workflow:
   {input_gh_rest_api_base_url}/repos/:owner/:repo/actions/workflows/:workflow_id/runs
   :workflow_id can also be :workflow_file_name (e.g., 'main.yml')
   Get :run_id from this

3) Get names and statuses of jobs in specific run:
   {input_gh_rest_api_base_url}/repos/:owner/:repo/actions/runs/:run_id/jobs
   Match found required GitHub Actions runs found in 1)

4) Wait and do 3) again until required GitHub Actions jobs have "status": "completed"
   If "conclusion" in inputs provided through `--acceptable-conclusion`
   (default: "success") YAY
   Otherwise, FAIL this action

"""
import argparse
import json
import logging
import os
import sys
from time import sleep, time
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

from push_action.cache import IN_MEMORY_CACHE
from push_action.utils import (
    api_request,
    get_branch_statuses,
    get_required_actions,
    get_required_checks,
    get_workflow_run_jobs,
    remove_branch,
)
from push_action.validate import validate_conclusions

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Dict


LOGGER = logging.getLogger("push_action.run")


def wait() -> None:
    """Wait until status checks have finished"""
    required_statuses = get_branch_statuses(IN_MEMORY_CACHE["args"].ref)
    actions_required = get_required_actions(required_statuses)
    _ = get_required_checks(
        required_statuses
    )  # TODO: Currently not implemented  # pylint: disable=fixme

    print(
        f"""
Configuration:
    interval: {IN_MEMORY_CACHE['args'].wait_interval!s} seconds
    timeout: {IN_MEMORY_CACHE['args'].wait_timeout!s} minutes
    required status checks: {required_statuses}
        of which are:
            GitHub Action-related: {len(actions_required)}
            Third-party checks: {len(_)}
""",
        flush=True,
    )

    start_time = time()
    unsuccessful_jobs = []
    while (time() - start_time) < (60 * IN_MEMORY_CACHE["args"].wait_timeout):
        # Iterate over all jobs, removing completed jobs from the list
        for job in actions_required.copy():
            if job["status"] == "completed":
                # Job is completed
                actions_required.remove(job)

                if (
                    job.get("conclusion", "")
                    not in IN_MEMORY_CACHE["acceptable_conclusions"]
                ):
                    # Job is completed unsuccessfully
                    if IN_MEMORY_CACHE["args"].fail_fast:
                        # Fail fast
                        raise RuntimeError(
                            f"Required check {job['name']} completed with conclusion "
                            f"{job['conclusion']!r} (not part of the acceptable "
                            "conclusions: "
                            f"{', '.join(IN_MEMORY_CACHE['acceptable_conclusions'])})."
                            f"\n{job}"
                        )

                    unsuccessful_jobs.append(job)

        if not actions_required:
            # All jobs are completed
            print("All required GitHub Actions jobs complete!", flush=True)
            break

        # Some jobs have not yet completed
        print(
            f"{len(actions_required)} required GitHub Actions jobs have not yet "
            f"completed!\nWaiting {IN_MEMORY_CACHE['args'].wait_interval} seconds ...",
            flush=True,
        )
        sleep(IN_MEMORY_CACHE["args"].wait_interval)

        # Update job statuses for all still running jobs
        run_ids = {job["run_id"] for job in actions_required}
        actions_required = []
        for run_id in run_ids:
            actions_required.extend(
                [
                    job
                    for job in get_workflow_run_jobs(run_id, new_request=True)
                    if job["name"] in required_statuses
                ]
            )

    if unsuccessful_jobs:
        raise RuntimeError(
            "Required checks completed with a conclusion not part of the acceptable "
            f"conclusions ({', '.join(IN_MEMORY_CACHE['acceptable_conclusions'])}):\n"
            f"{unsuccessful_jobs}"
        )


def unprotect_reviews() -> None:
    """Remove pull request review protection for target branch"""
    # Save current protection settings
    url = (
        f"/repos/{os.getenv('GITHUB_REPOSITORY', '')}/branches"
        f"/{IN_MEMORY_CACHE['args'].ref}/protection/required_pull_request_reviews"
    )
    response = api_request(url)

    if not isinstance(response, dict):
        raise TypeError(
            f"Expected response to be a dict, instead it was of type {type(response)}"
        )

    data = {
        "dismiss_stale_reviews": response.get("dismiss_stale_reviews", False),
        "require_code_owner_reviews": response.get("require_code_owner_reviews", False),
        "required_approving_review_count": response.get(
            "required_approving_review_count", 1
        ),
    }

    repository_info = api_request(f"/repos/{os.getenv('GITHUB_REPOSITORY', '')}")

    if not isinstance(repository_info, dict):
        raise TypeError(
            "Expected repository_info to be a dict, instead it was of type "
            f"{type(repository_info)}"
        )

    if "organization" in repository_info:
        # This key is only allowed for organization repositories
        data["dismissal_restrictions"] = {
            "users": [
                _.get("login")
                for _ in response.get("dismissal_restrictions", {}).get("users", [])
            ],
            "teams": [
                _.get("slug")
                for _ in response.get("dismissal_restrictions", {}).get("teams", [])
            ],
        }

    with open("tmp_protection_rules.json", "w", encoding="utf8") as handle:
        json.dump(data, handle)

    # Remove protection
    api_request(
        url, http_request="delete", expected_status_code=204, check_response=False
    )


def protect_reviews() -> None:
    """Re-add pull request review protection for target branch"""
    # Retrieve data
    with open("tmp_protection_rules.json", encoding="utf8") as handle:
        data = json.load(handle)

    # Add protection
    url = (
        f"/repos/{os.getenv('GITHUB_REPOSITORY', '')}/branches"
        f"/{IN_MEMORY_CACHE['args'].ref}/protection/required_pull_request_reviews"
    )
    api_request(
        url,
        http_request="patch",
        expected_status_code=200,
        check_response=False,
        json=data,
    )


def protected_branch(branch: str) -> str:
    """Determine whether or not `branch` is a protected branch.

    Return a non-empty string if it is protected, otherwise return an empty string.
    """
    url = f"/repos/{os.getenv('GITHUB_REPOSITORY', '')}/branches/{branch}"
    response: "Dict[str, Any]" = api_request(url)  # type: ignore[assignment]

    if "protected" not in response:
        raise RuntimeError(
            f"Information regarding whether the branch {branch} is protected cannot be "
            "retrieved."
        )

    return "protected" if response["protected"] else ""


def compile_origin_url() -> str:
    """Compile the git remote 'origin' URL for the repository."""
    compiled_url = ""

    for required_env_vars in [
        "GITHUB_SERVER_URL",
        "GITHUB_REPOSITORY",
        "GITHUB_ACTOR",
        "INPUT_TOKEN",
    ]:
        if required_env_vars not in os.environ:
            raise RuntimeError(
                f"Required rnvironment variable {required_env_vars} is not set."
            )

    base_url = os.getenv("GITHUB_SERVER_URL", "")
    split_base_url = urlsplit(base_url)

    if not (split_base_url.scheme or split_base_url.netloc):
        raise RuntimeError(
            f"Could not determine scheme and netloc from GITHUB_SERVER_URL: {base_url}"
        )

    # Add scheme
    compiled_url += f"{split_base_url.scheme}://"

    # Add username and token
    compiled_url += os.getenv("GITHUB_ACTOR", "")
    compiled_url += f":{os.getenv('INPUT_TOKEN', '')}"

    # Add netloc
    compiled_url += f"@{split_base_url.netloc}"

    # Add path (repository)
    compiled_url += f"/{os.getenv('GITHUB_REPOSITORY', '')}.git"

    return compiled_url


def main() -> None:
    """Main function to run this module"""
    # Handle inputs
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--token",
        type=str,
        help="GitHub Token from ${{ secrets.GITHUB_TOKEN }}",
        required=True,
    )
    parser.add_argument(
        "--ref",
        type=str,
        help="Target ref branch for the push",
        required=True,
    )
    parser.add_argument(
        "--temp-branch",
        type=str,
        help="Temporary branch name for the action",
        required=True,
    )
    parser.add_argument(
        "--wait-timeout",
        type=int,
        help=(
            "Time (in minutes) of how long the wait_for_checks should run before "
            "timing out"
        ),
        default=15,
    )
    parser.add_argument(
        "--wait-interval",
        type=int,
        help=(
            "Time interval (in seconds) between each new check in the wait_for_checks "
            "run"
        ),
        default=30,
    )
    parser.add_argument(
        "--acceptable-conclusion",
        type=str,
        help=(
            "Acceptable conclusion for the wait_for_checks run to be considered "
            "successful"
        ),
        action="append",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help=(
            "Whether or not to fail fast (i.e., exit immediately) if one of the "
            "checks fails. Only valid with the wait_for_checks action."
        ),
    )
    parser.add_argument(
        "ACTION",
        type=str,
        help="The action to do",
        choices=[
            "wait_for_checks",
            "remove_temp_branch",
            "unprotect_reviews",
            "protect_reviews",
            "protected_branch",
            "create_origin_url",
        ],
    )

    IN_MEMORY_CACHE["args"] = parser.parse_args()

    LOGGER.debug("Parsed args: %s", IN_MEMORY_CACHE["args"])

    fail = ""
    try:
        if IN_MEMORY_CACHE["args"].ACTION == "wait_for_checks":
            # Ensure that the acceptable conclusions are valid
            IN_MEMORY_CACHE["acceptable_conclusions"] = validate_conclusions(
                IN_MEMORY_CACHE["args"].acceptable_conclusion
            )

            wait()
        elif IN_MEMORY_CACHE["args"].ACTION == "remove_temp_branch":
            remove_branch(IN_MEMORY_CACHE["args"].temp_branch)
        elif IN_MEMORY_CACHE["args"].ACTION == "unprotect_reviews":
            unprotect_reviews()
        elif IN_MEMORY_CACHE["args"].ACTION == "protect_reviews":
            protect_reviews()
        elif IN_MEMORY_CACHE["args"].ACTION == "protected_branch":
            print(protected_branch(IN_MEMORY_CACHE["args"].ref), end="", flush=True)
        elif IN_MEMORY_CACHE["args"].ACTION == "create_origin_url":
            print(compile_origin_url(), end="", flush=True)
        else:
            raise RuntimeError(f"Unknown ACTIONS {IN_MEMORY_CACHE['args'].ACTION!r}")

    except Exception as exc:  # pylint: disable=broad-except
        fail = f"{exc.__class__.__name__}: {exc}"

    sys.exit(fail or None)
