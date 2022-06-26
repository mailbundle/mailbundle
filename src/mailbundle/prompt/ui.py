# -*- encoding: utf-8 -*-
import re
import typing as T

from InquirerPy import inquirer

from mailbundle.prompt.utils import clear_screen, list_from_input
from mailbundle.prompt.validators import ValidateInterval


VALID_QUERY = re.compile(r'^(.*) = (.*)$')


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
    if inquirer.confirm(
        "Do you want to specify additional notmuch queries on unread emails?",
        default=False,
    ).execute():
        add_q: T.Dict[T.Text, T.Text] = {}
        additional_queries = inquirer.text(
            "Specify additional notmuch queries, one per line, in the format 'query_name = query' (esc-enter to confirm and save, ctrl-c to skip)",
            validate=validate_query,
            multiline=True,
            raise_keyboard_interrupt=False,
            mandatory=False,
        ).execute()
        print(additional_queries)
        for q in additional_queries.split("\n"):
            if q:
                name, query = VALID_QUERY.match(q.strip()).groups()
                add_q[name] = query

        sidebar["additionalQueries"] = add_q

    return sidebar


def validate_query(query: T.Text) -> bool:
    for line in query.split("\n"):
        if line:
            res = VALID_QUERY.match(line.strip())
            if res:
                if len(res.groups()) != 2:
                    return False

    return True


if __name__ == "__main__":
    from pprint import pprint as pp
    ui = ask_ui()
    pp(ui)
