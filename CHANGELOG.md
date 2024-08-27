## v1.1.2 (2024-08-27)

### Fix

- upload properly documentation on read the docs

## v1.1.1 (2024-08-27)

### Fix

- use main as release branch
- search user using parent class and not buggy derived method

## v1.1.0 (2023-03-05)

### Feat

- create a Makefile, read type map from file, read status map from file and add link from Jira to Clickup if provided

## v1.0.2 (2023-01-09)

## v1.0.1 (2020-12-12)

### Fix

- **inputs**: expect user input in a new line

## v1.0.0 (2020-12-12)

### Feat

- **bump**: properly use commitizen in order to bump version
- **configuration**: provide ClickUp and JIRA project information using user input and not cli arguments
- **user-input**: support user defined mappings for ticket statuses
- **user-input**: support user defined inputs for ticket types
- **field-support**: support subtasks and comments in migration
- **structure**: create project structure

### Fix

- **ClickUp-throttling**: add proper sleep between requests on ClickUp in order to ensure the rate limit of requests is the proper one
- **jira**: fix query in JIRA using summary field
