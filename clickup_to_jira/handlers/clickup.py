from logging import getLogger
from time import sleep

from pyclickup import ClickUp

from clickup_to_jira.comment import Comment

logger = getLogger(__name__)


class ClickUpHandler(ClickUp):
    def get_task_comments(self, task):
        self.api_url = self.api_url.replace("v1", "v2")
        path = f"task/{task.id}/comment/?"
        raw_comment_dict = self.get(path)
        self.api_url = self.api_url.replace("v2", "v1")
        if not isinstance(raw_comment_dict, dict):
            return []
        comment_list = []
        for raw_comment in raw_comment_dict["comments"]:
            comment_list.append(
                Comment(
                    id=raw_comment.get("id"),
                    text=raw_comment.get("comment_text"),
                    commenter=raw_comment.get("user").get("email"),
                )
            )
        return comment_list

    def get_click_up_tickets(self, team, space, project, lst=None):
        """
        Get all ClickUp tickets.

        :param str team: The team to check for tickets on
        :param str space: The space to look for tickets on
        :param str project: The project to look for tickets on
        :param str lst: The list to look for tickets on
        :return: The list of tickets
        :rtype: list(Ticket)
        """
        logger.info("get clickup tickets")
        cur_team = list(filter(lambda x: team in x.name, self.teams))[0]
        cur_space = list(filter(lambda x: space in x.name, cur_team.spaces))[0]
        cur_project = list(
            filter(lambda x: project in x.name, cur_space.projects)
        )[0]
        if not lst:
            tasks = cur_project.get_all_tasks(
                include_closed=True, subtasks=True
            )
        else:
            cur_list = list(
                filter(lambda x: lst in x.name, cur_project.lists)
            )[0]
            tasks = cur_list.get_all_tasks(include_closed=True, subtasks=True)
        for task in tasks:
            task.comments = None

        for task in tasks:
            logger.info(f"Retrieving task {task.name}")
            sleep(0.1)
            task.comments = self.get_task_comments(task)
            try:
                task.parent = list(
                    filter(lambda x: x.id == task.parent, tasks)
                )[0].name
            except IndexError:
                logger.info("Issue has no parent")
                task.parent = None
        sorted_tasks = list()
        for task in tasks:
            if task.parent:
                sorted_tasks.append(task)
            else:
                sorted_tasks.insert(0, task)

        return sorted_tasks
