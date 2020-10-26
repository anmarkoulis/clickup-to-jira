from pyclickup import ClickUp


class ClickUpHandler(ClickUp):
    def get_click_up_tickets(self, team, space, project, lst):
        """
        Get all ClickUp tickets.

        :param str team: The team to check for tickets on
        :param str space: The space to look for tickets on
        :param str project: The project to look for tickets on
        :param str lst: The list to look for tickets on
        :return: The list of tickets
        :rtype: list(Ticket)
        """
        cur_team = list(filter(lambda x: team in x.name, self.teams))[0]
        cur_space = list(filter(lambda x: space in x.name, cur_team.spaces))[0]
        cur_project = list(
            filter(lambda x: project in x.name, cur_space.projects)
        )[0]
        cur_list = list(filter(lambda x: lst in x.name, cur_project.lists))[0]

        return cur_list.get_all_tasks(include_closed=True)
