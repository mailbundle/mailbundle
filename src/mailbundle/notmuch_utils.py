# -*- encoding: utf-8 -*-
import collections
import json
import os
import subprocess
import typing as T


def _notmuch_config_path(basepath: T.Text) -> T.Text:
    return os.path.normpath(os.path.join(basepath, "config", "notmuch-config"))


def all_tags(basepath: T.Text, query: T.Text = "*") -> T.List[T.Text]:
    """Retrieve all tags already stored by notmuch"""
    mailpath = os.path.join(basepath, "mail")
    notmuch_store_path = os.path.join(mailpath, ".notmuch")

    if os.path.isdir(mailpath) and os.path.isdir(notmuch_store_path):
        p = subprocess.Popen(
            ["notmuch", "search", "--output=tags", query],
            env=dict(NOTMUCH_CONFIG=_notmuch_config_path(basepath)),
            stdout=subprocess.PIPE,
        )
        out, _ = p.communicate()
        out = out.decode("utf8")
        return out.split("\n")

    return []


def all_tags_repeated(
    basepath: T.Text, query: T.Text = "*"
) -> T.Generator[T.Text, None, None]:
    mailpath = os.path.join(basepath, "mail")
    notmuch_store_path = os.path.join(mailpath, ".notmuch")

    if not (os.path.isdir(mailpath) and os.path.isdir(notmuch_store_path)):
        yield from []

    p = subprocess.Popen(
        [
            "notmuch",
            "--config",
            _notmuch_config_path(basepath),
            "search",
            "--output=summary",
            "--format=json",
            query,
        ],
        stdout=subprocess.PIPE,
    )
    out, _ = p.communicate()
    result = out.decode("utf8")
    if result:
        data = json.loads(result)
    else:
        data = []

    for message in data:
        yield from message.get("tags", [])


def tags_in_sidebar(
    basepath: T.Text, variables: T.Dict[T.Text, T.Any]
) -> T.List[T.Text]:
    """
    Retrieve the tags to be displayed in the sidebar of mutt
    """
    query = _safe_get(variables, ["sidebar", "tagsQuery"])
    if not query:
        query = _safe_get(variables, ["search", "defaultPeriod"])

    def ok_tag(tag: str) -> bool:
        if not tag.startswith("lists/"):
            return False
        # In my experience, lists with numeric names are newsletters
        if tag.split("/", 1)[1].isdigit():
            return False
        return True

    c = collections.Counter(
        t for t in all_tags_repeated(basepath, query or "") if ok_tag(t)
    )
    return [tag for tag, _ in c.most_common(10)]


def _safe_get(
    nested_dict: T.Dict[T.Any, T.Any], keys: T.List[T.Text]
) -> T.Optional[T.Any]:
    d = nested_dict
    for k in keys[:-1]:
        v = d.get(k)
        if v is None:
            return None
        d = v

    return d.get(keys[-1])
