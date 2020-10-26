import logging
import os
from argparse import ArgumentParser


def initialize_logging():
    """
    Initialize logging configuration.

    :param dict config_dict: The configuration dictionary
    """
    logging.basicConfig(
        level="ERROR",
        format=os.getenv(
            "LOGGING_FORMAT",
            "%(asctime)s %(name)-12s:" " %(levelname)-" "8s -  " "%(message)s",
        ),
    )
    logging.getLogger(__name__).setLevel(os.getenv("LOGGING_LEVEL", "INFO"))
    logging.getLogger(__name__).propagate = True


def get_cli_arguments():
    """
    Get CLI arguments.

    :return: The arguments
    :rtype: dict
    """
    parser = ArgumentParser(
        description="Setup ClickUp and JIRA ticket parameters."
    )
    parser.add_argument(
        "-TEAM", type=str, help="Team to look for tickets on", required=True
    )
    parser.add_argument(
        "-SPACE", type=str, help="Space to look for tickets on", required=True
    )
    parser.add_argument(
        "-PROJECT",
        type=str,
        help="Project to look for tickets on",
        required=False,
    )
    parser.add_argument(
        "-LIST",
        type=str,
        help="Lists to look for tickets on",
        required=True,
    )
    parser.add_argument(
        "-JIRA_PROJECT",
        type=str,
        help="JIRA project to add tickets on",
        required=True,
    )

    return parser.parse_args()
