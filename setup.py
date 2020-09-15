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

with open(TOP_DIR.joinpath("README.md")) as handle:
    README = handle.read()

with open(TOP_DIR.joinpath("requirements.txt")) as handle:
    REQUIREMENTS = handle.read()

with open(TOP_DIR.joinpath("requirements_dev.txt")) as handle:
    REQUIREMENTS_DEV = handle.read()


setup(
    name="push-action",
    version=version[0],
    url="https://github.com/CasperWA/push-protected",
    license="MIT",
    author="Casper Welzel Andersen",
    author_email="casper+github@welzel.nu",
    description="Push local workflow commit(s) to protected branches with required status checks.",
    long_description=README,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.8",
    install_requires=REQUIREMENTS,
    extras_require={"dev": REQUIREMENTS_DEV},
    entry_points={"console_scripts": ["push-action=push_action.run:main"]},
)
