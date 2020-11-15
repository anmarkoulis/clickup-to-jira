![CI](https://github.com/anmarkoulis/clickup-to-jira/workflows/CI/badge.svg)
 [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
# Clickup to JIRA Converter

## Description

This project is a small utility that helps migrating tasks from Clickup to JIRA.

## Installation

In order to use the package please install it by running the following command in the directory where the `setup.py` is found:

```bash
pip install .
```

## Execution

After installing the library run the following command.

```bash
migrate_to_jira [params]
```
### Execution Arguments

You may use the following command to view all the execution arguments

```bash
migrate_to_jira -h
```

The options presented are the following:

```bash
usage: migrate_to_jira [-h] -TEAM TEAM -SPACE SPACE -PROJECT PROJECT [-LIST LIST] -JIRA_PROJECT JIRA_PROJECT

Setup ClickUp and JIRA ticket parameters.

optional arguments:
  -h, --help            show this help message and exit
  -TEAM TEAM            Team to look for tickets on
  -SPACE SPACE          Space to look for tickets on
  -PROJECT PROJECT      Project to look for tickets on
  -LIST LIST            Lists to look for tickets on
  -JIRA_PROJECT JIRA_PROJECT
                        JIRA project to add tickets on

```

Keep in mind that the following environmental variables need to have a proper value.

1. `JIRA_URL`
1. `JIRA_API_KEY`
1. `JIRA_USER`
1. `CLICK_UP_API_KEY`
1. `LOGGING_FORMAT`
1. `LOGGING_LEVEL`
