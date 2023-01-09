from unittest import TestCase

from clickup_to_jira.utils import (
    get_item_from_user_input,
    get_with_to_specify_outcome,
)
from mock import MagicMock, patch


class TestUtils(TestCase):
    @patch("builtins.input")
    def test_get_item_from_user_input_happy_path(self, get_input):

        item_1 = MagicMock()
        item_1_name = "Item 1"
        item_1.name = item_1_name
        item_2 = MagicMock()
        item_2_name = "Item 2"
        item_2.name = item_2_name

        selection_list = [item_1, item_2]

        get_input.return_value = item_2_name

        output = get_item_from_user_input("item", selection_list)

        self.assertEqual(output, item_2)
        get_input.assert_called_once()

    @patch("builtins.input")
    def test_get_item_from_user_input_first_error_then_correct(
        self, get_input
    ):
        item_1 = MagicMock()
        item_1_name = "Item 1"
        item_1.name = item_1_name
        item_2 = MagicMock()
        item_2_name = "Item 2"
        item_2.name = item_2_name

        selection_list = [item_1, item_2]

        get_input.side_effect = ["Error", item_2_name]

        output = get_item_from_user_input("item", selection_list)

        self.assertEqual(output, item_2)
        self.assertEqual(get_input.call_count, 2)

    @patch("clickup_to_jira.utils.get_with_to_specify_outcome")
    @patch("builtins.input")
    def test_get_item_from_user_input_none(self, get_input, outcome):
        item_1 = MagicMock()
        item_1_name = "Item 1"
        item_1.name = item_1_name
        item_2 = MagicMock()
        item_2_name = "Item 2"
        item_2.name = item_2_name

        selection_list = [item_1, item_2]

        get_input.side_effect = ["Error", item_2_name]
        outcome.return_value = True
        allow_none = True

        output = get_item_from_user_input("item", selection_list, allow_none)

        self.assertEqual(output, None)
        self.assertEqual(get_input.call_count, 0)
        outcome.assert_called_once_with("item")

    @patch("builtins.input")
    def test_get_with_to_specify_outcome_y(self, get_input):
        get_input.side_effect = ["Y"]

        output = get_with_to_specify_outcome("item")

        self.assertEqual(output, False)
        self.assertEqual(get_input.call_count, 1)

    @patch("builtins.input")
    def test_get_with_to_specify_outcome_n(self, get_input):
        get_input.side_effect = ["N"]

        output = get_with_to_specify_outcome("item")

        self.assertEqual(output, True)
        self.assertEqual(get_input.call_count, 1)

    @patch("builtins.input")
    def test_get_with_to_specify_outcome_error_y(self, get_input):
        get_input.side_effect = ["Error", "Y"]

        output = get_with_to_specify_outcome("item")

        self.assertEqual(output, False)
        self.assertEqual(get_input.call_count, 2)

    @patch("builtins.input")
    def test_get_with_to_specify_outcome_error_n(self, get_input):
        get_input.side_effect = ["Error", "N"]

        output = get_with_to_specify_outcome("item")

        self.assertEqual(output, True)
        self.assertEqual(get_input.call_count, 2)
