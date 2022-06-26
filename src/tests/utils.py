# -*- encoding: utf-8 -*-
import pytest

from mailbundle.utils.find_config import find_config, get_all_parents


@pytest.mark.parametrize(
    "orig,expected",
    [
        ("/", ["/"]),
        ("/a/b/c/d", ["/a/b/c/d", "/a/b/c", "/a/b", "/a", "/"]),
        ("/a/b/c/d/", ["/a/b/c/d", "/a/b/c", "/a/b", "/a", "/"]),
    ],
)
def test_get_all_parents(orig, expected):
    assert get_all_parents(orig) == expected


def test_find_config(tmpdir):
    filename = "mailbundler.json"

    root = tmpdir / "mailbundle"
    root.mkdir()
    conf = root / filename
    with open(conf, "w") as f:
        f.write("")

    assert find_config(str(root), filename) == conf

    sub = root / "sub"
    sub.mkdir()

    assert find_config(str(sub), filename) == conf

    subsub = sub / "sub"
    subsub.mkdir()

    assert find_config(str(subsub), filename) == conf
