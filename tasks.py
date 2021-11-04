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
    match = re.fullmatch(
        (
            r"v?(?P<version>[0-9]+(\.[0-9]+){2}"  # Major.Minor.Patch
            r"(-[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?"  # pre-release
            r"(\+[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?)"  # build metadata
        ),
        version,
    )
    if not match:
        sys.exit(
            "Error: Please specify version as "
            "'[v]Major.Minor.Patch(-Pre-Release+Build Metadata)'"
        )
    version: str = match.group("version")

    update_file(
        TOP_DIR / "push_action" / "__init__.py",
        (r"__version__ = .+", f'__version__ = "{version}"'),
    )

    print(f"Bumped version to {version} !")
