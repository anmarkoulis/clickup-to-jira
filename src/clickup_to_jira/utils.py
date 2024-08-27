import logging
import os


def initialize_logging():  # pragma: no cover
    """
    Initialize logging configuration.
    """
    logging.basicConfig(
        level="ERROR",
        format=os.getenv(
            "LOGGING_FORMAT",
            "%(asctime)s %(name)-12s:" " %(levelname)-" "8s -  " "%(message)s",
        ),
    )
    logging.getLogger(__name__).setLevel(os.getenv("LOGGING_LEVEL", "INFO"))
    logging.getLogger("clickup_to_jira").setLevel(
        os.getenv("LOGGING_LEVEL", "INFO")
    )
    logging.getLogger(__name__).propagate = True


def get_item_from_user_input(name, selection_list, allow_none=False):
    """
    Get proper item from list of items from user input.

    :param str name: The name of the parameter to be specified.
    :param list selection_list: The ClickUp entity to search in.
    :param bool allow_none: Allow the user to not specify a value.
    :return: The proper item
    :rtype: ClickUp.Team|ClickUp.Space|ClickUp.Project|ClickUp.list
    """
    if allow_none and get_with_to_specify_outcome(name):
        return None

    # Get item from user input
    item_names = [item.name for item in selection_list]
    item_input = input(
        f"Please provide the name of the {name} you want to "
        f"browse for tickets. Eligible options are"
        f" {item_names} :\n"
    )

    # Add mapping if not exists
    if item_input not in item_names:
        while True:
            item_input = input(
                f"{item_input} is not a valid choice. "
                f"Please provide one of {item_names} :\n"
            )
            if item_input in item_names:
                return list(
                    filter(lambda x: item_input in x.name, selection_list)
                )[0]
    else:
        return list(filter(lambda x: item_input in x.name, selection_list))[0]


def get_with_to_specify_outcome(name):
    """
    Get if user does not wish to specify an outcome.

    :param str name: The name of the parameter which is allowed to not be
        set.
    :return: Allow none ot not
    :rtype: bool
    """
    accepted_inputs = ["Y", "N"]
    item_input = input(
        f"Do you wish to specify a {name}. If so please press Y. Else"
        f" press N : \n"
    )

    # Add mapping if not exists
    if item_input not in accepted_inputs:
        while True:
            item_input = input(
                f"{item_input} is not a valid choice. "
                f"Please provide one of {accepted_inputs} : \n"
            )
            if item_input == "Y":
                return False
            elif item_input == "N":
                return True

    else:
        if item_input == "Y":
            return False
        elif item_input == "N":
            return True
