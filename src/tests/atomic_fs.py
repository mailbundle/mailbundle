# -*- encoding: utf-8 -*-
import pytest

from mailbundle.utils.atomic_fs import atomic_fs, AtomicFailure


def test_atomic_success(tmpdir):
    CONTENT = "test"
    FNAME = "dest.txt"

    d = tmpdir / "mailbunde"
    d.mkdir()

    with atomic_fs(str(d)) as tmp_d:
        tmp_f = f"{tmp_d}/{FNAME}"

        with open(tmp_f, "w") as tmp_fp:
            tmp_fp.write(CONTENT)

    f = d / FNAME
    assert f.read_text("utf-8") == CONTENT


def test_atomic_failure(tmpdir):
    ex = Exception("oops")

    def boom():
        raise ex

    d = tmpdir / "mailbunde"
    d.mkdir()

    with pytest.raises(AtomicFailure) as e:
        with atomic_fs(str(d)):
            boom()

    assert e.value.unwrap() == ex
