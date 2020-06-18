from pathlib import Path
import re
from setuptools import setup, find_packages

TOP_DIR = Path(__file__).parent.resolve()
with open(TOP_DIR.joinpath("push_action/__init__.py"), "r") as handle:
    for line in handle.readlines():
        version = re.findall(r'__version__ = "(.*)"', line)
        if version:
            break
    else:
        raise RuntimeError("Could not determine version from push_action/__init__.py")


setup(
    name="push-action",
    version=version[0],
    url="https://github.com/CasperWA/push-with-status-checks-action",
    license="MIT",
    author="Casper Welzel Andersen",
    author_email="casper+github@welzel.nu",
    description="Push local workflow commit(s) to protected branches with required status checks.",
    long_description=open(TOP_DIR.joinpath("README.md")).read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.8",
    install_requires=["requests~=2.24"],
    extras_require={"dev": ["black~=19.10b0", "pre-commit~=2.5"]},
    entry_points={"console_scripts": ["push-action=push_action.run:main"]},
)
