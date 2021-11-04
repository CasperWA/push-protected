"""Utility `invoke` tasks for the repository.

Tasks here are based on the [`invoke`](https://pyinvoke.org) package.
"""
from pathlib import Path
import re
import sys
from typing import TYPE_CHECKING

try:
    from invoke import task
except ImportError:
    sys.exit("'invoke' MUST be installed to run these tasks.")

if TYPE_CHECKING:
    from typing import Tuple


TOP_DIR = Path(__file__).parent.resolve()


def update_file(filename: Path, sub_line: "Tuple[str, str]", strip: str = None) -> None:
    """Utility function for tasks to read, update, and write files"""
    lines = [
        re.sub(sub_line[0], sub_line[1], line.rstrip(strip))
        for line in filename.read_text().splitlines()
    ]
    filename.write_text("\n".join(lines) + "\n")


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
