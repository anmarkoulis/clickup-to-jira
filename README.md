![CI](https://github.com/anmarkoulis/clickup-to-jira/workflows/CI/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Documentation Status](https://readthedocs.org/projects/clickup-to-jira/badge/?version=latest)](https://clickup-to-jira.readthedocs.io/en/latest/?badge=latest)
# ClickUp to JIRA Converter

## Description

This project is a small utility that helps migrating tasks from ClickUp to JIRA.

## Installation

In order to use the package please install it by running the following command in the directory where the `setup.py` is found:

```bash
pip install .
```

## Execution

After installing the library run the following command.

```bash
migrate_to_jira
```

Keep in mind that the following environmental variables need to have a proper value.

|Environmental Variable|Required|Default|Description                                          |
|----------------------|--------|-------|-----------------------------------------------------|
|`JIRA_URL`            |True    |None   |The base URL for JIRA API                            |
|`JIRA_API_KEY`        |True    |None   |The API key created for accessing JIRA               |
|`JIRA_USER`           |True    |None   |Email of the JIRA user the API key belongs to        |
|`CLICKUP_API_KEY`     |True    |None   |The API key created for accessing ClickUp            |
|`LOGGING_FORMAT`      |False   |%(asctime)s %(name)-12s:" " %(levelname)-" "8s -  " "%(message)s|The format of the application logs|
|`LOGGING_LEVEL`       |False   |INFO   |The logging level of the application
