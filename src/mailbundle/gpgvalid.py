#!/usr/bin/env python3
from email.utils import parseaddr
from subprocess import check_output

F = {"kind": 0, "valid": 1, "email": 9, "id": 4}
ALL_VALIDITY = "-mfu"
cmd = ["gpg", "--batch", "--with-colons", "--list-keys"]


def _valid_ids(validities):
    for line in check_output(cmd).decode("utf8").split("\n"):
        fields = line.split(":")
        if fields[F["kind"]] == "pub" and fields[F["valid"]] in validities:
            yield fields[F["id"]]


def _id_to_emails(longid):
    _cmd = cmd + ["0x" + longid]
    for line in check_output(_cmd).decode("utf8").split("\n"):
        fields = line.split(":")
        if fields[F["kind"]] == "uid":
            yield fields[F["email"]]


def _email_to_address(fullmail):
    '''takes John Doe <jondo@yeah.baz> and returns "jondo@yeah.baz"'''
    return parseaddr(fullmail)[1]


### sum of previous ones
def valid_emails(min_validity):
    if not min_validity[0] in ALL_VALIDITY:
        raise ValueError("Validities are -unknown, marginal, full, ultimate")
    validities = ALL_VALIDITY[ALL_VALIDITY.find(min_validity[0]) :]
    l = []
    for longid in _valid_ids(validities):
        for email in _id_to_emails(longid):
            l.append(_email_to_address(email))
    return l


if __name__ == "__main__":
    ACCEPTED_VALIDITY = ALL_VALIDITY[ALL_VALIDITY.find("f") :]
    for address in valid_emails(ACCEPTED_VALIDITY):
        print(address)
