# -*- encoding: utf-8 -*-
from contextlib import contextmanager
from shutil import copytree
from tempfile import mkdtemp
import typing as T


@contextmanager
def atomic_fs(dst: T.Text) -> T.Generator[T.Text, None, None]:
    tmp_dir = mkdtemp()

    try:
        yield tmp_dir
    except Exception as e:
        raise AtomicFailure(e, tmp_dir)
    finally:
        copytree(tmp_dir, dst, dirs_exist_ok=True)


class AtomicFailure(Exception):
    def __init__(self, wrapped: Exception, tmp_dir: T.Text) -> None:
        self.inner = wrapped
        self.tmp_dir = tmp_dir

    def __str__(self) -> T.Text:
        return f"atomic operation on filesystem failed: {self.inner}"

    def unwrap(self) -> Exception:
        return self.inner
