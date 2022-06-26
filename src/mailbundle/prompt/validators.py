# -*- encoding: utf-8 -*-
import re
import socket
import typing as T

from prompt_toolkit.validation import Validator, ValidationError

from mailbundle.prompt.utils import list_from_input


class Singleton(object):
    _instances: T.Dict[T.Text, T.Any] = {}

    def __new__(cls, name, *args, **kwargs):
        if name not in cls._instances:
            cls._instances[name] = super().__new__(cls, *args, **kwargs)

        return cls._instances[name]


class UniqueName(Singleton, Validator):
    def __init__(self, name: T.Text) -> None:
        self.set = set()
        self.name = name

    def validate(self, doc: T.Any) -> None:
        try:
            if doc.text is None or len(doc.text) == 0:
                raise ValueError

            name = str(doc.text)
        except ValueError:
            raise ValidationError(
                message="Please enter a valid name", cursor_position=len(doc.text),
            )

        if name in self.set:
            raise ValidationError(
                message="Please enter another name, the one provided is already in use",
                cursor_position=len(name),
            )

        self.set.add(name)

    def get_names(self) -> T.List[T.Text]:
        return list(self.set)


class ValidateResolvingDomain(Validator):
    def validate(self, doc: T.Any) -> None:
        try:
            addr = str(doc.text)
            socket.gethostbyname(addr)
        except (ValueError, socket.gaierror):
            raise ValidationError(
                message="Please enter a valid address", cursor_position=len(doc.text),
            )


class ValidateListWithRe(Validator):
    def validate(self, doc: T.Any) -> None:
        try:
            names = list_from_input(doc.text)
            if len(names) == 0:
                raise ValueError
        except ValueError:
            raise ValidationError(
                message="Provide a non empty list", cursor_position=len(doc.text),
            )

        for name in names:
            if self._re.match(name) is None:
                raise ValidationError(
                    message=f"{name} is not a valid {self._kind}",  # noqa: E501
                    cursor_position=len(doc.text),
                )


class ValidateDomains(ValidateListWithRe):
    _kind = "domain"
    _re = re.compile(
        r"""(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""")  # noqa: E501


class ValidateEmails(ValidateListWithRe):
    _kind = "email"
    _re = re.compile(r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""")  # noqa: E501


class ValidateInterval(Validator):
    _re = re.compile(r"""^\d+[dwMY]$""")

    def validate(self, doc: T.Any) -> None:
        if self._re.match(doc.text) is None:
            raise ValidationError(
                message=f"{doc.text} is not a valid time interval",
                cursor_position=len(doc.text),
            )
