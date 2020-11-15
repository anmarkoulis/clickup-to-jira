from logging import getLogger
from time import sleep

from pyclickup import ClickUp

from clickup_to_jira.comment import Comment

logger = getLogger(__name__)

SLEEP_PER_COMMENT = 0.1


class ClickUpHandler(ClickUp):
    """
    Class responsible for retrieving info from ClickUp
    """

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

        tasks = self.get_tasks_from_click_up(team, space, project, lst)
        tasks_with_comments = self.add_comments_to_tasks(tasks)
        tasks_with_parent = self.add_parent_to_tasks(tasks_with_comments)

        return self.get_sorted_tasks(tasks_with_parent)

    def get_tasks_from_click_up(self, team, space, project, lst=None):
        """
        Get ClickUp tasks.

        :param str team: The team name in ClickUp
        :param str space: The space name in ClickUp
        :param str project: The project name in ClickUp
        :param str|None lst: The list name in ClickUp if provided
        :return: The list of ClickUp tasks
        :rtype: ClickUp(Task)
        """
        cur_team = list(filter(lambda x: team in x.name, self.teams))[0]
        cur_space = list(filter(lambda x: space in x.name, cur_team.spaces))[0]
        cur_project = list(
            filter(lambda x: project in x.name, cur_space.projects)
        )[0]

        if not lst:
            return cur_project.get_all_tasks(
                include_closed=True, subtasks=True
            )
        else:
            cur_list = list(
                filter(lambda x: lst in x.name, cur_project.lists)
            )[0]
            return cur_list.get_all_tasks(include_closed=True, subtasks=True)

    def add_comments_to_tasks(self, tasks):
        """
        Add comments to tasks.

        :param list(Task) tasks: The tasks on which comments are added
        :return: The updated tasks
        :rtype: list(Task)
        """
        for task in tasks:
            logger.info(f"Retrieving task {task.name}")
            sleep(SLEEP_PER_COMMENT)
            task.comments = self.get_task_comments(task)
        return tasks

    @staticmethod
    def add_parent_to_tasks(tasks):
        """
        Add parent to tasks.

        :param list(Task) tasks: The tasks on which parent is added
        :return: The updated tasks
        :rtype: list(Task)
        """
        for task in tasks:
            task.parent = None

        for task in tasks:
            logger.info(f"Retrieving father for task {task.name}")
            try:
                task.parent = list(
                    filter(lambda x: x.id == task.parent, tasks)
                )[0].name
            except IndexError:
                logger.info("Issue has no parent")
                task.parent = None
        return tasks

    def get_task_comments(self, task):
        """
        Get task comments.

        :param Task task: The task whose comments are to be retrieved
        :return: The list of task comments
        :rtype: list(Comment)
        """
        # Get comments from ClickUp
        self.api_url = self.api_url.replace("v1", "v2")
        path = f"task/{task.id}/comment/?"
        raw_comment_dict = self.get(path)
        self.api_url = self.api_url.replace("v2", "v1")
        if not isinstance(raw_comment_dict, dict):
            return []

        # Populate Comment DataClass
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

    @staticmethod
    def get_sorted_tasks(tasks):
        """
        Get ordered tasks with tasks before subtasks.

        :param list(Task) tasks: The tasks list

        :return: The ordered tasks list
        :rtype: list(Task)
        """
        sorted_tasks = list()
        for task in tasks:
            if task.parent:
                sorted_tasks.append(task)
            else:
                sorted_tasks.insert(0, task)
        return sorted_tasks
