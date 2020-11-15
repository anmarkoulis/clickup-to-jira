import os
from unittest import TestCase

from mock import MagicMock, patch

from clickup_to_jira.scripts.migrate import main


class TestMigrate(TestCase):
    @patch.dict(
        os.environ,
        {
            "CLICKUP_API_KEY": "apikey",  # pragma: allowlist secret
            "JIRA_URL": "jiraurl",
            "JIRA_USER": "user",
            "JIRA_API_KEY": "apikey",  # pragma: allowlist secret
        },
    )
    @patch("clickup_to_jira.scripts.migrate.ClickUpHandler")
    @patch("clickup_to_jira.scripts.migrate.JIRAHandler")
    @patch("clickup_to_jira.scripts.migrate.ClickUpToJIRAConverter")
    @patch("clickup_to_jira.scripts.migrate.get_cli_arguments")
    @patch("clickup_to_jira.scripts.migrate.initialize_logging")
    def test_main(self, logging, cli_args, converter, jira, clickup):
        cli_params = MagicMock()
        cli_params.TEAM = "team"
        cli_params.SPACE = "space"
        cli_params.PROJECT = "project"
        cli_params.LIST = "list"
        cli_params.JIRA_PROJECT = "jira_project"

        clickup_tickets = MagicMock()
        converted_tickets = MagicMock()

        cli_args.return_value = cli_params
        clickup().get_click_up_tickets.return_value = clickup_tickets
        converter().convert.return_value = converted_tickets

        main()

        logging.assert_called_once()
        cli_args.assert_called_once()
        clickup().get_click_up_tickets.assert_called_once_with(
            cli_params.TEAM,
            cli_params.SPACE,
            cli_params.PROJECT,
            cli_params.LIST,
        )
        converter().convert.assert_called_once_with(
            clickup_tickets,
        )
        jira().create_jira_issues.assert_called_once_with(
            converted_tickets, cli_params.JIRA_PROJECT
        )
