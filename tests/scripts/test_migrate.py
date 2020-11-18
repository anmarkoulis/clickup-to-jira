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
    @patch("clickup_to_jira.scripts.migrate.initialize_logging")
    def test_main(self, logging, converter, jira, clickup):
        clickup_tickets = MagicMock()
        converted_tickets = MagicMock()

        clickup().get_click_up_tickets.return_value = clickup_tickets
        converter().convert.return_value = converted_tickets

        main()

        logging.assert_called_once()
        converter().convert.assert_called_once_with(
            clickup_tickets,
        )
        jira().create_jira_issues.assert_called_once_with(
            converted_tickets,
        )
