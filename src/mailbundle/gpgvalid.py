# -*- encoding: utf-8 -*-
from email.utils import parseaddr
from subprocess import check_output
import typing as T

import click


F = {"kind": 0, "valid": 1, "email": 9, "id": 4}
ALL_VALIDITY = "-mfu"
cmd = ["gpg", "--batch", "--with-colons", "--list-keys"]


def _valid_ids(validities: T.Text) -> T.Generator[T.Text, None, None]:
    """Yields the key ids of the valid keys in the db"""
    for line in check_output(cmd).decode("utf8").split("\n"):
        fields = line.split(":")
        if fields[F["kind"]] == "pub" and fields[F["valid"]] in validities:
            yield fields[F["id"]]


def _id_to_emails(longid: T.Text) -> T.Generator[T.Text, None, None]:
    """Yields the emails associated the the given longid"""
    _cmd = cmd + ["0x" + longid]
    for line in check_output(_cmd).decode("utf8").split("\n"):
        fields = line.split(":")
        if fields[F["kind"]] == "uid":
            yield fields[F["email"]]


def _email_to_address(fullmail: T.Text) -> T.Text:
    '''takes John Doe <jondo@yeah.baz> and returns "jondo@yeah.baz"'''
    return parseaddr(fullmail)[1]


# TODO: support specifying the --homedir
def valid_emails(min_validity: T.Text) -> T.List[T.Text]:
    """Given the minimum allowed validity level, returns the list of valid emails"""
    if not min_validity[0] in ALL_VALIDITY:
        raise ValueError("Validities are -unknown, marginal, full, ultimate")

    validities = ALL_VALIDITY[ALL_VALIDITY.find(min_validity[0]) :]

    valid_ids: T.List[T.Text] = []
    for longid in _valid_ids(validities):
        for email in _id_to_emails(longid):
            valid_ids.append(_email_to_address(email))

    return valid_ids


# TODO: support specifying the --homedir
@click.command("gpg-valid")
@click.option(
    "-v",
    "--validity",
    envvar="MAILBUNDLE_MIN_GPG_VALIDITY",
    default=None,
    help="The minimum validity allowed",
)
def gpg_valid_cli(validity: T.Optional[T.Text]) -> None:
    ACCEPTED_VALIDITY = ALL_VALIDITY[ALL_VALIDITY.find(validity or "-") :]
    try:
        for address in valid_emails(ACCEPTED_VALIDITY):
            print(address)
    except ValueError as e:
        print(e)
