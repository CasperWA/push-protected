from pathlib import Path
import re
import sys
from typing import Tuple

try:
    from invoke import task
except ImportError:
    sys.exit("'invoke' MUST be installed to run these tasks.")


TOP_DIR = Path(__file__).parent.resolve()


def update_file(filename: str, sub_line: Tuple[str, str], strip: str = None):
    """Utility function for tasks to read, update, and write files"""
    with open(filename, "r") as handle:
        lines = [
            re.sub(sub_line[0], sub_line[1], line.rstrip(strip)) for line in handle
        ]

    with open(filename, "w") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


@task(help={"version": "push_action package version to set"})
def update_version(_, version=""):
    """Update push_action package version"""
    if version:
        if version.startswith("v"):
            version = version[1:]
        if re.match(r"[0-9]+(\.[0-9]+){2}.*", version) is None:
            sys.exit(
                f"Error: Passed `version` ([v]{version}) does to match SemVer versioning."
            )
    else:
        sys.exit("No `version` provided.")

    update_file(
        TOP_DIR.joinpath("push_action/__init__.py"),
        (r"__version__ = .+", f'__version__ = "{version}"'),
    )

    print(f"Bumped version to {version} !")
