import argparse
import os
import sys
from time import sleep, time

from git import Repo

from push_action.utils import (
    api_request,
    branch_exists,
    get_branch_statuses,
    get_required_actions,
    get_required_checks,
    get_workflow_run_jobs,
    IN_MEMORY_CACHE,
    remove_branch,
)


def wait():
    """Wait until status checks have finished"""
    required_statuses = get_branch_statuses(IN_MEMORY_CACHE["args"].ref)
    actions_required = get_required_actions(required_statuses)
    _ = get_required_checks(required_statuses)  # TODO: Currently not implemented

    start_time = time()
    while True and ( time() - start_time ) < ( 60 * IN_MEMORY_CACHE["args"].wait_timeout ):
        sleep(IN_MEMORY_CACHE["args"].wait_interval)

        for job in actions_required:
            if job["status"] != "completed":
                break
        else:
            # All jobs are completed
            unsuccessful_jobs = [
                _ for _ in actions_required if _.get("conclusion", "") == "success"
            ]
            break

        # Some jobs have not yet completed
        run_ids = {_["run_id"] for _ in actions_required}
        actions_required = []
        for run in run_ids:
            actions_required.extend([
                _ for _ in get_workflow_run_jobs(run, new_request=True)
                if _["name"] in required_statuses
            ])
    
    if unsuccessful_jobs:
        raise RuntimeError(f"Required checks complete unsuccessfully:\n{unsuccessful_jobs}")


def inital_checks():
    """Initial checks for how to run workflow"""
    if not branch_exists(IN_MEMORY_CACHE["args"].ref):
        raise RuntimeError(
            "Target branch could not be found in the repository "
            f"{IN_MEMORY_CACHE['args'].repo!r}.\n"
            "NOTE: Handling tags has not yet been implemented."
        )


def create_temp_branch(name: str):
    """Create temporary branch"""
    commit_shas = IN_MEMORY_CACHE["args"].commits.split(" ")
    repo = Repo("/github/workspace/target_repo")

    create_commit_url = f"/repos/{IN_MEMORY_CACHE['args'].repo}/git/commits"
    for commit_sha in commit_shas:
        commit = repo.commit(commit_sha)
        data = {
            "message": commit.message,
            "tree": str(commit.tree),
            "parents": [str(_) for _ in commit.parents],
            "author": {
                "name": commit.author.name,
                "email": commit.author.email,
                "date": commit.authored_datetime.strftime("%Y-%M-%dT%H:%M:%SZ")
            },
            "committer": {
                "name": commit.committer.name,
                "email": commit.committer.email,
                "date": commit.committed_datetime.strftime("%Y-%M-%dT%H:%M:%SZ")
            },
        }
        api_request(
            create_commit_url, http_request="post", expected_status_code=201, data=data
        )

    create_ref_url = f"/repos/{IN_MEMORY_CACHE['args'].repo}/git/refs"
    data = {
        "ref": f"refs/heads/{name}",
        "sha": commit_shas[0],
    }
    api_request(
        create_ref_url, http_request="post", expected_status_code=201, data=data
    )


def main():
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
        "--repo",
        type=str,
        help="Repository name to push to",
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
        help="Time (in minutes) of how long the wait_for_checks should run before timing out",
        default=15
    )
    parser.add_argument(
        "--wait-interval",
        type=str,
        help="Time interval (in seconds) between each new check in the wait_for_checks run",
        default=30,
    )
    parser.add_argument(
        "--commits",
        type=str,
        help="List of commit SHAs added locally",
    )
    parser.add_argument(
        "ACTION",
        type=str,
        help="The action to do",
        choices=["wait_for_checks", "remove_temp_branch", "create_temp_branch"],
    )

    global IN_MEMORY_CACHE
    IN_MEMORY_CACHE["args"] = parser.parse_args()

    fail = False
    try:
        inital_checks()

        if IN_MEMORY_CACHE["args"].ACTION == "wait_for_checks":
            wait()
        elif IN_MEMORY_CACHE["args"].ACTION == "remove_temp_branch":
            remove_branch(IN_MEMORY_CACHE['args'].temp_branch)
        elif IN_MEMORY_CACHE["args"].ACTION == "create_temp_branch":
            create_temp_branch(IN_MEMORY_CACHE['args'].temp_branch)
        else:
            raise RuntimeError(f"Unknown ACTIONS {IN_MEMORY_CACHE['args'].ACTION!r}")
    except RuntimeError as exc:
        fail = repr(exc)
    finally:
        del IN_MEMORY_CACHE

    if fail:
        sys.exit(fail)
    else:
        sys.exit()

"""
1) Get required statuses for branch (GitHub Actions jobs / third party status checks) from:
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
