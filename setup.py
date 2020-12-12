import setuptools

version = "1.0.1"


def get_requirements_from_file(requirements_file):
    """
    Get requirements from file.

    :param str req_file: Name of file to parse for requirements.
    :return: List of requirements
    :rtype: list(str)
    """
    requirements = []
    with open(requirements_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith(("#", "-e")):
                requirements.append(line)

    return requirements


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="clickup-to-jira",
    version=version,
    author="Antonis Markoulis",
    author_email="amarkoulis@hotmail.com",
    description="A utility that helps migrating from Clickup to JIRA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=["tests", "docs"]),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "migrate_to_jira = clickup_to_jira.scripts.migrate:main"
        ],
    },
    python_requires=">=3.8",
    zip_safe=True,
    install_requires=get_requirements_from_file("requirements.txt"),
    tests_require=get_requirements_from_file("requirements-tests.txt"),
)
