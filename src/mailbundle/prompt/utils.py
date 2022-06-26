# -*- encoding: utf-8 -*-
import os
import typing as T


def clear_screen() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')


def list_from_input(input_text: T.Text) -> T.List[T.Text]:
    return [name for name in str(input_text).split("\n") if name != ""]
