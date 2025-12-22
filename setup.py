#!/usr/bin/env python

from setuptools import setup, find_packages
try:
    from pipenv.project import Project
    from pipenv.utils import convert_deps_to_pip

    pfile = Project().parsed_pipfile
    requirements = convert_deps_to_pip(pfile["packages"], r=False)
    test_requirements = convert_deps_to_pip(pfile["dev-packages"], r=False)
except ImportError:
    # get the requirements from the requirements.txt
    requirements = [line.strip()
                    for line in open("requirements.txt")
                    if line.strip() and not line.startswith("#") and not line.startswith("-")]
    # get the test requirements from the test_requirements.txt
    test_requirements = [line.strip()
                         for line in
                         open("dev-requirements.txt")
                         if line.strip() and not line.startswith("#") and not line.startswith("-")]

readme = open("README.rst").read()
history = open("HISTORY.rst").read().replace(".. :changelog:", "")
version = open(".VERSION").read()


setup(
    name="""azureenergylabelercli""",
    version=version,
    description="""A cli to help generate energy label for Azure tenant, subscriptions and resource groups.""",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/x-rst",
    author="""Sayantan Khanra""",
    author_email="""skhanra@schubergphilis.com""",
    url="""https://github.com/schubergphilis/azureenergylabelercli""",
    packages=find_packages(where=".", exclude=("tests", "hooks")),
    package_dir={"""azureenergylabelercli""":
                 """azureenergylabelercli"""},
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords="""azureenergylabelercli """,
    entry_points = {
                   "console_scripts": [
                       # enable this to automatically generate a script in /usr/local/bin called myscript that points to your
                       #  azureenergylabelercli.azureenergylabelercli:main method
                       "azure-energy-labeler = azure_energy_labeler_cli:main",
                   ]},
    scripts=["azure_energy_labeler_cli.py"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.14",
        ],
    test_suite="tests",
    tests_require=test_requirements,
)
