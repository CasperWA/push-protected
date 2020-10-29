import os
from typing import Union, List
from urllib.parse import urljoin

try:
    import simplejson as json
except ImportError:
    import json

import requests

from push_action.cache import IN_MEMORY_CACHE


REQUEST_TIMEOUT = 10  # in seconds
API_V3_BASE = "https://api.github.com"


def api_request(
    url: str,
    http_request: str = "get",
    expected_status_code: int = 200,
    check_response: bool = True,
    **kwargs,
) -> Union[List[dict], dict, None]:
    """Perform GitHub API v3 request

    kwargs will be passed on to requests.<http_request> method.
    """
    url = urljoin(API_V3_BASE, url)
    try:
        requests_action = getattr(requests, http_request)
    except AttributeError:
        raise RuntimeError(
            f"Unknown HTTP Request: {http_request}. Not supported by requests package."
        )

    try:
        response = requests_action(
            url,
            headers={
                "Authorization": f"token {IN_MEMORY_CACHE['args'].token}",
                "Accept": "application/vnd.github.v3+json",
            },
            timeout=REQUEST_TIMEOUT,
            **kwargs,
        )
    except (
        requests.exceptions.ConnectionError,
        requests.exceptions.ConnectTimeout,
    ) as exc:
        raise RuntimeError(f"Couldn't connect to {url!r}.\n{exc!r}")

    if response.status_code != expected_status_code:
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            response_json = "<FAILED TO JSONIFY RESPONSE>"
        message = f"Response did not return the expected status code from request {url!r}.\nStatus code: {response.status_code} (expected: {expected_status_code}).\nResponse:\n{response_json}"

        if response.status_code in range(200, 300):
            import warnings

            warnings.warn(message)
        else:
            if "X-Ratelimit-Remaining" in response.headers and not int(
                response.headers["X-Ratelimit-Remaining"]
            ):
                from time import time

                raise RuntimeError(
                    "The remaining number of requests to GitHub has reached 0 (out of "
                    f"{dict(response.headers).get('X-Ratelimit-Limit', 'N/A')}). "
                    f"You can try again in {dict(response.headers).get('X-Ratelimit-Reset', 0) - time()!s} s."
                )
            raise RuntimeError(message)

    if check_response:
        try:
            response = response.json()
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Failed to jsonify response.\n{exc!r}")

    return response


def remove_branch(name: str) -> None:
    """Remove named branch in repository"""
    delete_ref_url = (
        f"/repos/{os.getenv('GITHUB_REPOSITORY', '')}/git/refs/heads/{name}"
    )
    api_request(
        delete_ref_url,
        http_request="delete",
        expected_status_code=204,
        check_response=False,
    )


def get_branch_statuses(name: str, new_request: bool = False) -> List[str]:
    """Get required statuses for branch

    These may be GitHub Actions jobs and/or third-party status checks.
    """
    cache_name = "get_branch_statuses"

    if cache_name not in IN_MEMORY_CACHE or new_request:
        branch_statuses_url = (
            f"/repos/{os.getenv('GITHUB_REPOSITORY', '')}/branches/{name}"
        )
        response: dict = api_request(branch_statuses_url)

        if response["protected"]:
            IN_MEMORY_CACHE[cache_name] = (
                response["protection"]
                .get("required_status_checks", {})
                .get("contexts", [])
            )
        else:
            IN_MEMORY_CACHE[cache_name] = []

    return IN_MEMORY_CACHE[cache_name]


def get_workflow_runs(workflow_id: int, new_request: bool = False) -> List[dict]:
    """Return list of GitHub Actions workflow runs"""
    cache_name = "get_workflow_runs"

    if (
        cache_name not in IN_MEMORY_CACHE
        or workflow_id not in IN_MEMORY_CACHE.get(cache_name, {})
        or new_request
    ):
        workflow_runs_url = f"/repos/{os.getenv('GITHUB_REPOSITORY', '')}/actions/workflows/{workflow_id}/runs"
        response: dict = api_request(
            workflow_runs_url, params={"branch": IN_MEMORY_CACHE["args"].temp_branch}
        )

        if cache_name in IN_MEMORY_CACHE:
            IN_MEMORY_CACHE[cache_name][workflow_id] = response.get("workflow_runs", [])
        else:
            IN_MEMORY_CACHE[cache_name] = {
                workflow_id: response.get("workflow_runs", [])
            }

    return IN_MEMORY_CACHE[cache_name][workflow_id]


def get_workflow_run_jobs(run_id: int, new_request: bool = False) -> List[dict]:
    """Return list of GitHub Actions workflow runs"""
    cache_name = "get_workflow_run_jobs"

    if (
        cache_name not in IN_MEMORY_CACHE
        or run_id not in IN_MEMORY_CACHE.get(cache_name, {})
        or new_request
    ):
        workflow_jobs_url = (
            f"/repos/{os.getenv('GITHUB_REPOSITORY', '')}/actions/runs/{run_id}/jobs"
        )
        response: dict = api_request(workflow_jobs_url)

        if cache_name in IN_MEMORY_CACHE:
            IN_MEMORY_CACHE[cache_name][run_id] = response.get("jobs", [])
        else:
            IN_MEMORY_CACHE[cache_name] = {run_id: response.get("jobs", [])}

    return IN_MEMORY_CACHE[cache_name][run_id]


def get_required_actions(statuses: List[str], new_request: bool = False) -> List[dict]:
    """Get subset of statuses that belong to GitHub Actions jobs"""
    cache_name = "get_required_actions"

    if cache_name not in IN_MEMORY_CACHE or new_request:
        if not statuses:
            IN_MEMORY_CACHE[cache_name] = []
        else:
            workflows_url = (
                f"/repos/{os.getenv('GITHUB_REPOSITORY', '')}/actions/workflows"
            )
            response: dict = api_request(workflows_url)

            runs = []
            for workflow in response["workflows"]:
                runs.extend(get_workflow_runs(workflow["id"]))

            jobs = []
            for run in runs:
                jobs.extend(get_workflow_run_jobs(run["id"]))

            IN_MEMORY_CACHE[cache_name] = [
                _ for _ in jobs if _.get("name", "") in statuses
            ]

    return IN_MEMORY_CACHE[cache_name]


def get_required_checks(statuses: List[str], new_request: bool = False) -> List[str]:
    """Get subset of statuses that belong to third-party status checks

    TODO: Currently not implemented
    """
    return []
