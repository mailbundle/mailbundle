# -*- encoding: utf-8 -*-
import typing as T

from InquirerPy import inquirer

from mailbundle.prompt.utils import clear_screen, list_from_input
from mailbundle.prompt.validators import ValidateInterval


def ask_ui() -> T.Dict[T.Text, T.Any]:
    result: T.Dict[T.Text, T.Any] = {}

    clear_screen()

    if inquirer.confirm(
        "Do you want to specify search parameters?",
        default=True,
    ).execute():
        result["search"] = ask_search()

    if inquirer.confirm(
        "Do you want to specify compose parameters?",
        default=True,
    ).execute():
        result["compose"] = ask_compose()

    if inquirer.confirm(
        "Do you want to specify sidebar parameters?",
        default=True,
    ).execute():
        result["sidebar"] = ask_sidebar()

    return result


def ask_search() -> T.Dict[T.Text, T.Any]:
    search: T.Dict[T.Text, T.Any] = {}

    default_period = inquirer.text(
        "Insert the default search interval (e.g. 10d, 3w, 1M, 2Y; ctrl-c to skip)",
        validate=ValidateInterval(),
        default="1M",
        raise_keyboard_interrupt=False,
        mandatory=False,
    ).execute()

    search = {"defaultPeriod": default_period}

    search["queryAppend"] = {}
    for inbox in ["Unread", "INBOX", "Personal", "Recent"]:
        inbox_val = inquirer.text(
            f"Extend notmuch query for {inbox} (ctrl-c to skip)",
            raise_keyboard_interrupt=False,
            mandatory=False,
        ).execute()
        if inbox_val:
            search["queryAppend"][inbox] = inbox_val

    recent_period = inquirer.text(
        "Set the period for 'Recent' notmuch query (ctrl-c to skip)",  # noqa: E501
        validate=ValidateInterval(),
        raise_keyboard_interrupt=False,
        mandatory=False,
    ).execute()
    if recent_period:
        search["recentPeriod"] = recent_period

    return search


def ask_compose() -> T.Dict[T.Text, T.Any]:
    compose: T.Dict[T.Text, T.Any] = {}

    words = inquirer.text(
        "Insert words to look for in email body to warn for missing attachments (ctrl-c to skip)",  # noqa. E501
        raise_keyboard_interrupt=False,
        mandatory=False,
        multiline=True,
    ).execute()
    if words:
        compose["words"] = list_from_input(words)

    editor = inquirer.text(
        "Specify editor to open when composing emails (ctrl-c to skip)",
        raise_keyboard_interrupt=False,
        mandatory=False,
    ).execute()
    if editor:
        compose["editor"] = editor

    return compose


def ask_sidebar() -> T.Dict[T.Text, T.Any]:
    sidebar: T.Dict[T.Text, T.Any] = {}

    if inquirer.confirm(
        "Do you want to use tags in the sidebar?",
        default=True,
    ).execute():
        sidebar["tagsEntries"] = True

        tags_query = inquirer.text(
            "Modify the tags query (ctrl-c to skip)",
            raise_keyboard_interrupt=False,
            mandatory=False,
        ).execute()
        if tags_query:
            sidebar["tagsQuery"] = tags_query

    return sidebar


if __name__ == "__main__":
    from pprint import pprint as pp
    ui = ask_ui()
    pp(ui)
