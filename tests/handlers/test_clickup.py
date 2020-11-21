from unittest import TestCase

from mock import MagicMock, patch

from clickup_to_jira.comment import Comment
from clickup_to_jira.handlers import ClickUpHandler


class TestClickUpHandler(TestCase):
    def setUp(self) -> None:
        self.handler = ClickUpHandler("key")

    def test_get_click_up_tickets(self):
        self.handler.get_tasks_from_click_up = MagicMock()
        self.handler.add_comments_to_tasks = MagicMock()
        self.handler.get_sorted_tasks = MagicMock()

        tasks = [MagicMock(), MagicMock()]
        self.handler.get_tasks_from_click_up.return_value = tasks
        tasks_comment = [MagicMock(), MagicMock()]
        self.handler.add_comments_to_tasks.return_value = tasks_comment
        sorted_tasks = [MagicMock()]
        self.handler.get_sorted_tasks.return_value = sorted_tasks

        result = self.handler.get_click_up_tickets()

        self.assertEqual(result, sorted_tasks)

        self.handler.get_tasks_from_click_up.assert_called_once_with()
        self.handler.add_comments_to_tasks.assert_called_once_with(tasks)
        self.handler.get_sorted_tasks.assert_called_once_with(tasks_comment)

    @patch("clickup_to_jira.handlers.clickup.get_item_from_user_input")
    def test_get_tasks_from_click_up(self, get_item):
        team = "team"
        space = "space"
        project = "project"
        lst = "lst"

        team_obj = MagicMock()
        space_obj = MagicMock()
        project_obj = MagicMock()
        lst_obj = MagicMock()

        team_obj.name = team
        team_obj.spaces = [space_obj]
        space_obj.name = space
        space_obj.projects = [project_obj]
        project_obj.name = project
        project_obj.lists = [lst_obj]
        lst_obj.name = lst

        get_item.side_effect = [team_obj, space_obj, project_obj, lst_obj]

        tasks = [MagicMock()]
        lst_obj.get_all_tasks.return_value = tasks

        self.handler._teams = [team_obj]

        output = self.handler.get_tasks_from_click_up()

        self.assertEqual(output, tasks)
        lst_obj.get_all_tasks.assert_called_once_with(
            include_closed=True, subtasks=True
        )

    @patch("clickup_to_jira.handlers.clickup.get_item_from_user_input")
    def test_get_tasks_from_click_up_no_lst(self, get_item):
        team = "team"
        space = "space"
        project = "project"

        team_obj = MagicMock()
        space_obj = MagicMock()
        project_obj = MagicMock()

        team_obj.name = team
        team_obj.spaces = [space_obj]
        space_obj.name = space
        space_obj.projects = [project_obj]
        project_obj.name = project

        get_item.side_effect = [team_obj, space_obj, project_obj, None]

        tasks = [MagicMock()]
        project_obj.get_all_tasks.return_value = tasks

        self.handler._teams = [team_obj]

        output = self.handler.get_tasks_from_click_up()

        self.assertEqual(output, tasks)
        project_obj.get_all_tasks.assert_called_once_with(
            include_closed=True, subtasks=True
        )

    def test_add_comments_to_tasks(self):
        comment = MagicMock()

        task = MagicMock()

        self.handler.get_task_comments = MagicMock()
        self.handler.get_task_comments.return_value = [comment]

        output = self.handler.add_comments_to_tasks([task])
        self.assertEqual(output, [task])
        self.assertEqual(task.comments, [comment])

    def test_get_task_comments_no_dict(self):
        task = MagicMock()
        task.id = 1
        comment_dict = []
        self.handler.get = MagicMock()
        self.handler.get.return_value = comment_dict

        output = self.handler.get_task_comments(task)
        self.assertEqual(output, [])
        self.handler.get.assert_called_once_with(f"task/{task.id}/comment/?")

    def test_get_task_comments_sunny_day(self):
        task = MagicMock()
        task.id = 1
        comment_id = 1
        comment_text = "text"
        email = "user@mail.com"
        comment_dict = {
            "comments": [
                {
                    "id": comment_id,
                    "comment_text": comment_text,
                    "user": {"email": email},
                }
            ]
        }
        self.handler.get = MagicMock()
        self.handler.get.return_value = comment_dict

        ref_comment_list = [
            Comment(id=comment_id, text=comment_text, commenter=email)
        ]
        output = self.handler.get_task_comments(task)
        self.assertEqual(output, ref_comment_list)
        self.handler.get.assert_called_once_with(f"task/{task.id}/comment/?")

    def test_get_sorted_tasks(self):
        task_1 = MagicMock()
        task_1.parent = True

        task_2 = MagicMock()
        task_2.parent = False

        task_3 = MagicMock()
        task_3.parent = True

        output = self.handler.get_sorted_tasks([task_1, task_2, task_3])

        self.assertEqual(output, [task_2, task_1, task_3])
