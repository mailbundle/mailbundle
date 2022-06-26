# -*- encoding: utf-8 -*-
import typing as T

from InquirerPy import inquirer
from InquirerPy.validator import NumberValidator

from mailbundle.prompt.validators import ValidateEmails
from mailbundle.prompt.utils import clear_screen


def ask_hooks(groups: T.List[T.Text]) -> T.List[T.Dict[T.Text, T.Any]]:
    result: T.List[T.Dict[T.Text, T.Any]] = []
    ask_other_hook = True
    while ask_other_hook:
        rules: T.Dict[T.Text, T.Any] = {}
        clear_screen()

        group = inquirer.select(
            "Which group does this hook acts upon?",
            choices=groups,
        ).execute()

        encrypt = inquirer.confirm(
            "Always pgp encrypt the email for the recipient(s)?",
            default=False,
        ).execute()
        rules["encrypt"] = encrypt

        sign = inquirer.confirm(
            "Always pgp sign the email?",
            default=False,
        ).execute()
        rules["sign"] = sign

        from_addr = inquirer.text(
            "Set a default From for this group? (skip with ctrl-c)",
            validate=ValidateEmails(),
            raise_keyboard_interrupt=False,
            mandatory=False,
        ).execute()
        if from_addr:
            rules["from"] = from_addr

        score = inquirer.text(
            "Set a score for this group? (skip with ctrl-c)",
            validate=NumberValidator(float_allowed=False),
            raise_keyboard_interrupt=False,
            mandatory=False,
        ).execute()
        if score:
            rules["score"] = int(score)

        result.append({
            "group": group,
            "rules": rules,
        })

        ask_other_hook = inquirer.confirm(
            "Would you want to insert another hook?",
            default=True,
        ).execute()

    return result


if __name__ == "__main__":
    from pprint import pprint as pp
    hooks = ask_hooks(["group1", "group2", "group3"])
    pp(hooks)
