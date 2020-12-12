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
