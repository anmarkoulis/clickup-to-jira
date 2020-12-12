import json
import os

TAG_NAME = os.getenv("INPUT_TAG_NAME").split("refs/tags/")[1]
PATH_TO_CHANGELOG = os.getenv("INPUT_CHANGELOG")


def get_changelog_lines():
    """
    Read relevant files of changelog for specified tag.

    :return: The desired lines
    :rtype: list(str)
    """
    with open(PATH_TO_CHANGELOG, "r") as read_file:
        all_lines = read_file.readlines()
        changelog_lines = []
        read_line = False
        for line in all_lines:
            if f"## {TAG_NAME}" in line:
                read_line = True
                continue
            if read_line:
                if "## v" in line:
                    break
                else:
                    changelog_lines.append(line)
        return changelog_lines


if __name__ == "__main__":
    notes = get_changelog_lines()
    notes_dict = json.dumps({"notes": notes})
    print(f"::set-output name=notes::{notes_dict}")
