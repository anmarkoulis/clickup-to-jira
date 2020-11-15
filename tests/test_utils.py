from unittest import TestCase

from mock import patch

from clickup_to_jira.utils import get_cli_arguments


class TestUtils(TestCase):
    @patch("clickup_to_jira.utils.ArgumentParser")
    def test_get_cli_arguments(self, parser):
        get_cli_arguments()
        self.assertEqual(parser().add_argument.call_count, 5)
        parser().parse_args.assert_called_once()
