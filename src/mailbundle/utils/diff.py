# -*- encoding: utf-8 -*-

from __future__ import annotations
import argparse
from enum import Enum
import json
import os
import re
import sys
import typing as T

import click


class Status(Enum):
    ADDED = "+"
    REMOVED = "-"

    def is_added(self):
        return self is self.ADDED

    def is_removed(self):
        return self is self.REMOVED


class Folder(Enum):
    NEW = "new"
    CUR = "cur"


class Mailfile(object):
    uid: int
    flags: T.Set[T.Text]

    def __init__(self, uid: int, flags: T.Set[T.Text]) -> None:
        self.uid = uid
        self.flags = flags

    def __eq__(self, v: Mailfile):
        return v.uid == self.uid and v.flags == self.flags

    def __lt__(self, other: Mailfile) -> bool:
        return self.uid < other.uid

    def __repr__(self) -> T.Text:
        return f"Mailfile({','.join([str(self.uid), '' .join(self.flags)])})"

    @classmethod
    def from_filename(cls, filename: T.Text) -> Mailfile:
        parsed = re.search(
            r"\d+_\d+.\d+.[\w\d_\-\.]+,U=(\d+),FMD5=[\w\d]{32}(:2)?,(D?F?R?S?T?)",
            filename,
        )

        if parsed is None:
            raise ValueError

        uid = int(parsed[1])
        flags = set(c for c in parsed[3])

        return cls(uid, flags)


class Diff(object):
    file: Mailfile
    status: Status

    def __init__(self, file: Mailfile, status: Status) -> None:
        self.file = file
        self.status = status


class MailboxDiff(object):
    new: T.List[Diff]
    cur: T.List[Diff]

    def __init__(self, new: T.List[Diff], cur: T.List[Diff]) -> None:
        self.new = new
        self.cur = cur

    def __repr__(self) -> T.Text:
        return f"MailboxDiff({len(self.new)}, {len(self.cur)})"

    def _divide(
        self, folder: Folder
    ) -> T.Tuple[T.Dict[int, Mailfile], T.Dict[int, Mailfile]]:
        added = dict()
        removed = dict()

        for diff in getattr(self, folder.value):
            if diff.status.is_added():
                added[diff.file.uid] = diff.file
            else:
                removed[diff.file.uid] = diff.file

        return added, removed

    def added(self, folder: T.Union[T.Text, Folder]) -> T.List[Mailfile]:
        if isinstance(folder, str):
            folder = Folder(folder)

        added, removed = self._divide(folder)
        result = []

        for uid, file in added.items():
            if uid not in removed:
                result.append(file)

        return result

    def removed(self, folder: T.Union[T.Text, Folder]) -> T.List[Mailfile]:
        if isinstance(folder, str):
            folder = Folder(folder)

        added, removed = self._divide(folder)
        result = []

        for uid, file in removed.items():
            if uid not in added:
                result.append(file)

        return result

    def changed(self, folder: T.Union[T.Text, Folder]) -> T.List[Mailfile]:
        if isinstance(folder, str):
            folder = Folder(folder)

        added, removed = self._divide(folder)
        result = []

        for uid, file in removed.items():
            if uid in added:
                result.append(file)

        return result


class Mailbox(object):
    new: T.List[Mailfile]
    cur: T.List[Mailfile]

    def __init__(self, new: T.List[Mailfile], cur: T.List[Mailfile]) -> None:
        self.new = new
        self.cur = cur

    @staticmethod
    def _diff(set1: T.List[Mailfile], set2: T.List[Mailfile]) -> T.List[Diff]:
        result: T.List[Diff] = []

        for el in set1:
            try:
                set2.remove(el)
            except ValueError:
                result.append(Diff(el, Status.ADDED))

        for el in set2:
            result.append(Diff(el, Status.REMOVED))

        return result

    def diff(self, other: Mailbox) -> MailboxDiff:
        newdiff = self._diff(self.new, other.new)
        curdiff = self._diff(self.cur, other.cur)

        return MailboxDiff(newdiff, curdiff)

    @classmethod
    def from_path(cls, path: T.Text) -> Mailbox:
        dirs = os.listdir(path)
        if "cur" not in dirs or "new" not in dirs:
            raise ValueError(f"{path} is not a maildir")

        cur: T.List[Mailfile] = []
        for file in os.listdir(os.path.join(path, "cur")):
            try:
                cur.append(Mailfile.from_filename(file))
            except ValueError:
                print(f"Skipping malformed filename {file}", file=sys.stderr)

        new: T.List[Mailfile] = []
        for file in os.listdir(os.path.join(path, "new")):
            try:
                new.append(Mailfile.from_filename(file))
            except ValueError:
                print(f"Skipping malformed filename {file}", file=sys.stderr)

        return cls(new, cur)


class MailboxEncoder(json.JSONEncoder):
    def default(self, obj: T.Any) -> T.Any:
        if isinstance(obj, list):
            return [self.default(i) for i in obj]
        if isinstance(obj, dict):
            return dict((k, self.default(v)) for k, v in obj)
        if isinstance(obj, Mailbox) or isinstance(obj, MailboxDiff):
            return {
                "new": self.default(obj.new),
                "cur": self.default(obj.cur),
            }
        if isinstance(obj, Diff):
            return {
                "__type__": "diff",
                "file": self.default(obj.file),
                "diff": obj.status.value,
            }
        if isinstance(obj, Mailfile):
            return {
                "uid": obj.uid,
                "flags": "".join(sorted(obj.flags)),
            }

        return json.JSONEncoder.default(self, obj)


def diff(
    path1: T.Dict[T.Text, Mailbox], path2: T.Dict[T.Text, Mailbox]
) -> T.Dict[T.Text, MailboxDiff]:
    result: T.Dict[T.Text, MailboxDiff] = dict()
    mboxes1 = list(path1.keys())
    mboxes2 = list(path2.keys())

    for mbox in mboxes1:
        try:
            mboxes2.remove(mbox)
            result[mbox] = path1[mbox].diff(path2[mbox])
        except ValueError:
            pass

    for mbox in mboxes2:
        empty = Mailbox([], [])
        result[mbox] = empty.diff(path2[mbox])

    return result


def explore(basepath: T.Text) -> T.Dict[T.Text, Mailbox]:
    result: T.Dict[T.Text, Mailbox] = dict()
    for dir in os.listdir(basepath):
        try:
            result[dir] = Mailbox.from_path(os.path.join(basepath, dir))
        except ValueError:
            print(f"Skipping {dir}", file=sys.stderr)

    return result


@click.command("mailbox-diff", help="Compute the diff of two mailboxes")
@click.option(
    "-a",
    "--added",
    is_flag=True,
    help="Show only the files added in the second mailbox",
)
@click.option(
    "-r",
    "--removed",
    is_flag=True,
    help="Show only the files removed in the second mailbox",
)
@click.option(
    "-c",
    "--changed",
    is_flag=True,
    help="Show only the files changed in the second mailbox",
)
@click.argument("mailbox1", type=click.Path(exists=True))
@click.argument("mailbox2", type=click.Path(exists=True))
def main(
    added: bool, removed: bool, changed: bool, mailbox1: T.Text, mailbox2: T.Text
) -> None:
    if (added and removed) or (added and changed) or (removed and changed):
        click.echo(
            "Only one (optional) flag is allowed amongst --added, --removed, --changed",
            err=True,
            color=True,
        )
        sys.exit(-1)

    m1 = explore(mailbox1)
    m2 = explore(mailbox2)

    diff_result = diff(m1, m2)

    result = dict()

    if added:
        for k, v in diff_result.items():
            result[k] = {
                Folder.NEW.value: v.added(Folder.NEW),
                Folder.CUR.value: v.added(Folder.CUR),
            }
    elif removed:
        for k, v in diff_result.items():
            result[k] = {
                Folder.NEW.value: v.removed(Folder.NEW),
                Folder.CUR.value: v.removed(Folder.CUR),
            }
    elif changed:
        for k, v in diff_result.items():
            result[k] = {
                Folder.NEW.value: v.changed(Folder.NEW),
                Folder.CUR.value: v.changed(Folder.CUR),
            }
    else:
        result = diff_result

    click.echo(json.dumps(result, cls=MailboxEncoder))
