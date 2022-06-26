# -*- encoding: utf-8 -*-
import typing as T

from InquirerPy import inquirer

from mailbundle.prompt.utils import clear_screen
from mailbundle.prompt.validators import (
    UniqueName, ValidateResolvingDomain, ValidateEmails,
)
from mailbundle.utils.connection import resolve_endpoints


PASSWORD_KEY_MAP = {"plain password": "password", "command": "password_exec"}
UNIQUE_ACCOUNT = UniqueName("account")


def ask_accounts() -> T.Dict[T.Text, T.Any]:
    accounts: T.Dict[T.Text, T.Any] = {"accounts": [], "main": None}
    ask_other_account = True
    while ask_other_account:
        clear_screen()
        name = inquirer.text(
            "Insert the account name",
            validate=UNIQUE_ACCOUNT,
        ).execute()
        email = str(inquirer.text(
            "Please enter the email",
            validate=ValidateEmails(),
        ).execute())
        imap = smtp = None
        if inquirer.confirm(
            "Would you want us to try and find the connection parameters?",
            default=True,
        ).execute():
            imap, smtp = resolve_endpoints(email)
        else:
            imap = inquirer.text(
                "Insert the IMAP address",
                validate=ValidateResolvingDomain(),
            ).execute()
            smtp = inquirer.text(
                "Insert the SMTP address",
                validate=ValidateResolvingDomain(),
            ).execute()

        password_key_str = str(inquirer.select(
            "Choose among this kind of way to provide the password",
            choices=["plain password", "command"],
        ).execute())
        password_key = PASSWORD_KEY_MAP[password_key_str]

        password = None
        if password_key == "password":
            password = inquirer.secret(
                "Enter the account password",
            ).execute()
        elif password_key == "password_exec":
            password = inquirer.text(
                "Enter the command to retrieve the password",
            ).execute()

        accounts["accounts"].append({
            "name": name,
            "email": email,
            "imap_host": imap,
            "smtp_host": smtp,
            password_key: password,
        })

        ask_other_account = inquirer.confirm(
            "Do you want to insert a new account?",
            default=True,
        ).execute()

    main = inquirer.select(
        "Choose the main account",
        choices=UNIQUE_ACCOUNT.get_names(),
    ).execute()

    accounts["main"] = main

    return accounts


if __name__ == "__main__":
    from pprint import pprint as pp
    accounts = ask_accounts()
    pp(accounts)
