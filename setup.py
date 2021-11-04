"""Setup file for installing the `push-action` package.

Install the action by running:

```console
/path/to/push-protected$ pip install .
```

"""
from pathlib import Path
import re
from setuptools import setup, find_packages


TOP_DIR = Path(__file__).parent.resolve()

with open(TOP_DIR / "push_action" / "__init__.py", "r", encoding="utf8") as handle:
    for line in handle.readlines():
        version = re.findall(r'__version__ = "(.*)"', line)
        if version:
            break
    else:
        raise RuntimeError("Could not determine version from push_action/__init__.py")


setup(
    name="push-action",
    version=version[0],
    url="https://github.com/CasperWA/push-protected",
    license="MIT",
    author="Casper Welzel Andersen",
    author_email="casper+github@welzel.nu",
    description=(
        "Push local workflow commit(s) to protected branches with required status "
        "checks."
    ),
    long_description=(TOP_DIR / "README.md").read_text(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.8",
    install_requires=(TOP_DIR / "requirements.txt").read_text(),
    extras_require={"dev": (TOP_DIR / "requirements_dev.txt").read_text()},
    entry_points={"console_scripts": ["push-action=push_action.run:main"]},
)
