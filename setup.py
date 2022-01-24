# -*- encoding: utf-8 -*-

import os
from setuptools import setup, find_packages
import subprocess
import typing as T


def get_dependencies() -> T.List[T.Text]:
    dependencies: T.List[T.Text] = []

    with open("requirements.txt") as req:
        for line in req.readlines():
            clean_line = line.strip()
            if not clean_line.startswith("#"):
                dependencies.append(clean_line.strip("\n"))

    return dependencies


def get_version() -> T.Text:
    version = os.environ.get("MAILBUNDLE_VERSION")
    if version is not None:
        return version

    p = subprocess.run(
        ["git", "describe", "--match", '"v[0-9]*.[0-9]*.[0-9]*"', "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if p.returncode == 0 and p.stdout:
        return p.stdout.decode("ASCII")[1:]

    p = subprocess.run(
        ["git", "rev-list", "-1", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if p.returncode == 0 and p.stdout:
        commit = p.stdout.decode("ASCII").strip("\n")
        return f"0.0.0+{commit}"

    return "0.0.0+dev"


def get_readme_content() -> T.Text:
    with open("README.md") as r:
        content = r.read()

    return content or ""


LICENSE = "GPLv3"


setup(
    name="mailbundle",
    version=get_version(),
    description="A utility to read and send emails",
    long_description=get_readme_content(),
    long_description_content_type="text/markdown",
    author="boyska",
    author_email="piuttosto@logorroici.net",
    maintainer="blallo",
    maintainer_email="blallo@autistici.org",
    url="https://github.com/boyska/mailbundle",
    license=LICENSE,
    install_requires=get_dependencies(),
    extras_require={
        "dev": [
            "ipdb",
        ],
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "mailbundle = mailbundle.cli:main",
            "maildir-diff = mailbundle.utils.diff:main",
        ],
    },
)
