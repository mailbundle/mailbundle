# -*- encoding: utf-8 -*-
import re
import typing as T

from InquirerPy import inquirer

from mailbundle.prompt.validators import UniqueName, ValidateDomains, ValidateEmails
from mailbundle.prompt.utils import clear_screen, list_from_input


unique_name = UniqueName("group")


def ask_groups() -> T.Dict[T.Text, T.Any]:
    groups: T.Dict[T.Text, T.Any] = {}
    ask_other_group = True
    while ask_other_group:
        clear_screen()

        name = inquirer.text(
            "Choose the group name",
            validate=unique_name,
        ).execute()

        group = {}

        addr_list = inquirer.text(
            f"Input one address per line (esc-enter to confirm and save, ctrl-c to skip)",  # noqa: E501
            validate=ValidateEmails(),
            multiline=True,
            raise_keyboard_interrupt=False,
            mandatory=False,
        ).execute()
        if addr_list:
            group["to"] = list_from_input(addr_list)

        dom_list = inquirer.text(
            f"Input one domain per line (esc-enter to confirm and save, ctrl-c to skip)",  # noqa: E501
            validate=ValidateDomains(),
            multiline=True,
            raise_keyboard_interrupt=False,
            mandatory=False,
        ).execute()
        if dom_list:
            group["to_domains"] = list_from_input(dom_list)

        pgp_validity = inquirer.text(
            f"Input pgp validity conditions, one per line (esc-enter to confirm and save, ctrl-c to skip)",  # noqa: E501
            validate=lambda val: val.lower() in [
                "f", "m", "u", "-", "unknown", "marginal", "full", "ultimate",
            ],
            multiline=True,
            raise_keyboard_interrupt=False,
            mandatory=False,
        ).execute()
        if pgp_validity:
            group["pgp_validity"] = list_from_input(pgp_validity)

        if group:
            groups[name] = group

        ask_other_group = inquirer.confirm(
            "Would you want to insert another group?",
            default=True,
        ).execute()

    return groups


if __name__ == "__main__":
    from pprint import pprint as pp
    groups = ask_groups()
    pp(groups)
