![CI](https://github.com/anmarkoulis/clickup-to-jira/workflows/CI/badge.svg)
# Clickup to JIRA Converter

## Description

This project is a small utility that helps migrating from Clickup to JIRA.

## Installation

In order to use the package please install it by running the following command in the directory where the `setup.py` is found:

```bash
pip install .
```

## Execution

After installing the library run the following command.

```bash
./clickup_to_jira_migrate
```

Keep in mind that the following environmental variables need to have a proper value.

1. `JIRA_URL`
1. `JIRA_API_KEY`
1. `JIRA_USER`
1. `CLICK_UP_API_KEY`
1. `LOGGING_FORMAT`
1. `LOGGING_LEVEL`
