# -*- encoding: utf-8 -*-
import logging
import typing as T

try:
    from InquirerPy import inquirer

    from mailbundle.prompt.accounts import ask_accounts
    from mailbundle.prompt.groups import ask_groups
    from mailbundle.prompt.hooks import ask_hooks
    from mailbundle.prompt.ui import ask_ui
    from mailbundle.prompt.utils import clear_screen
    with_prompt = True
except ImportError as e:
    print(e)
    with_prompt = False


log = logging.getLogger("main")


def ask_variables() -> T.Dict[T.Text, T.Any]:
    if with_prompt:
        return _ask_variables()
    else:
        log.error("No configuration file found")
        return {}


def _ask_variables() -> T.Dict[T.Text, T.Any]:
    result: T.Dict[T.Text, T.Any] = {}

    # accounts
    accounts = ask_accounts()
    result["accounts"] = accounts

    clear_screen()

    # groups
    if inquirer.confirm(
        "Do you want to define groups?",
        default=True,
    ).execute():
        groups = ask_groups()
        if groups:
            result["groups"] = groups
            hooks = ask_hooks(list(groups.keys()))
            if hooks:
                result["hooks"] = hooks

    # ui
    ui = ask_ui()
    search = ui.get("search")
    if search:
        result["search"] = search

    compose = ui.get("compose")
    if compose:
        result["compose"] = compose

    sidebar = ui.get("sidebar")
    if sidebar:
        result["sidebar"] = sidebar

    # result
    return result


if __name__ == "__main__":
    from pprint import pprint as pp
    variables = ask_variables()
    pp(variables)
