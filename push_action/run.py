"""push_action.run

This is the main module implementing the CLI `push-action`.

The steps of progression for the whole of the action are the following:

1) Get required statuses for branch (GitHub Actions jobs / third party status checks)
   from:
   https://api.github.com/repos/:owner/:repo/branches/:branch
   protection -> required_status_checks -> contexts

2) Get GitHub Actions runs for specific workflow:
   https://api.github.com/repos/:owner/:repo/actions/workflows/:workflow_id/runs
   :workflow_id can also be :workflow_file_name (e.g., 'main.yml')
   Get :run_id from this

3) Get names and statuses of jobs in specific run:
   https://api.github.com/repos/:owner/:repo/actions/runs/:run_id/jobs
   Match found required GitHub Actions runs found in 1)

4) Wait and do 3) again until required GitHub Actions jobs have "status": "completed"
   If "conclusion": "success" YAY
   If "conclusion" != "success" FAIL this action

"""
import argparse
import json
import os
import sys
from time import sleep, time

from push_action.cache import IN_MEMORY_CACHE
from push_action.utils import (
    api_request,
    get_branch_statuses,
    get_required_actions,
    get_required_checks,
    get_workflow_run_jobs,
    remove_branch,
)


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
"""
    )

    start_time = time()
    unsuccessful_jobs = []
    while (time() - start_time) < (60 * IN_MEMORY_CACHE["args"].wait_timeout):
        for job in actions_required:
            if job["status"] != "completed":
                break
        else:
            # All jobs are completed
            print("All required GitHub Actions jobs complete!")
            unsuccessful_jobs = [
                _ for _ in actions_required if _.get("conclusion", "") != "success"
            ]
            break

        # Some jobs have not yet completed
        print(f"Waiting {IN_MEMORY_CACHE['args'].wait_interval} seconds ...")
        sleep(IN_MEMORY_CACHE["args"].wait_interval)

        run_ids = {_["run_id"] for _ in actions_required}
        actions_required = []
        for run in run_ids:
            actions_required.extend(
                [
                    _
                    for _ in get_workflow_run_jobs(run, new_request=True)
                    if _["name"] in required_statuses and _["status"] != "completed"
                ]
            )
        if actions_required:
            print(
                f"{len(actions_required)} required GitHub Actions jobs have not yet "
                "completed!"
            )

    if unsuccessful_jobs:
        raise RuntimeError(
            f"Required checks completed unsuccessfully:\n{unsuccessful_jobs}"
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
    with open("tmp_protection_rules.json", "r", encoding="utf8") as handle:
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

    Return branch if it is protected, otherwise return an empty string.
    """
    url = f"/repos/{os.getenv('GITHUB_REPOSITORY', '')}/branches/{branch}/protection"
    try:
        api_request(url)
    except RuntimeError:
        # Expected not to be protected
        return ""
    else:
        return branch


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
        help="Target ref (branch/tag) for the push",
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
        "ACTION",
        type=str,
        help="The action to do",
        choices=[
            "wait_for_checks",
            "remove_temp_branch",
            "unprotect_reviews",
            "protect_reviews",
            "protected_branch",
        ],
    )

    IN_MEMORY_CACHE["args"] = parser.parse_args()

    fail = ""
    try:
        if IN_MEMORY_CACHE["args"].ACTION == "wait_for_checks":
            wait()
        elif IN_MEMORY_CACHE["args"].ACTION == "remove_temp_branch":
            remove_branch(IN_MEMORY_CACHE["args"].temp_branch)
        elif IN_MEMORY_CACHE["args"].ACTION == "unprotect_reviews":
            unprotect_reviews()
        elif IN_MEMORY_CACHE["args"].ACTION == "protect_reviews":
            protect_reviews()
        elif IN_MEMORY_CACHE["args"].ACTION == "protected_branch":
            print(protected_branch(IN_MEMORY_CACHE["args"].ref), end="")
        else:
            raise RuntimeError(f"Unknown ACTIONS {IN_MEMORY_CACHE['args'].ACTION!r}")
    except RuntimeError as exc:
        fail = f"{exc.__class__.__name__}: {exc}"

    if fail:
        sys.exit(fail)
    else:
        sys.exit()
