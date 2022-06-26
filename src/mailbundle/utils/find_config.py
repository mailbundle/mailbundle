# -*- encoding: utf-8 -*-
import os
import stat
import typing as T


def find_config(cwd: T.Text, filename: T.Text) -> T.Optional[T.Text]:
    """
    This function is in charge of finding the configuration in all the parent paths.
    """
    for parent in get_all_parents(cwd):
        candidate = os.path.join(parent, filename)
        try:
            mode = os.stat(candidate).st_mode
            if stat.S_ISREG(mode):
                return candidate
        except FileNotFoundError:
            continue

    return None


def get_all_parents(path: T.Text) -> T.List[T.Text]:
    result = ["/"]
    acc = "/"
    for p in path.split("/"):
        if p == "":
            continue
        acc = os.path.join(acc, p)
        result.append(acc)

    return result[::-1]
