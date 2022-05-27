# -*- encoding: utf-8 -*-
import logging
import os
import shutil
import typing as T

from jinja2 import Environment, ChoiceLoader, FileSystemLoader, PackageLoader, Template
from jinja2.runtime import Context

try:
    from jinja2.utils import pass_context
except ImportError:
    from jinja2.filters import contextfilter

    pass_context = contextfilter

from mailbundle.gpgvalid import valid_emails


# TODO
DEFAULT_TEMPLATES_PATH = {}
DEFAULT_TEMPLATES_REL_PATH = os.path.join("assets", "templates")


@pass_context
def warn(ctx: Context, s: T.Text) -> T.Text:
    logging.getLogger(f"templates.{ctx.name.split('.')[0]}").warning(s)
    return ""


@pass_context
def info(ctx: Context, s: T.Text) -> T.Text:
    logging.getLogger(f"templates.{ctx.name.split('.')[0]}").info(s)
    return ""


@pass_context
def debug(ctx: Context, s: T.Text) -> T.Text:
    logging.getLogger(f"templates.{ctx.name.split('.')[0]}").debug(s)
    return ""


def prepare_env(env: Environment) -> Environment:
    """Endows the passed Environment with the necessary functionalities"""
    env.globals["gpg_valid"] = valid_emails

    env.filters["warn"] = warn
    env.filters["info"] = info
    env.filters["debug"] = debug
    env.tests["avail_bin"] = shutil.which

    return env


def get_jinja_env(custom_path: T.Text) -> Environment:
    """
    This function returns the jinja2.Environment which gives precedence to the
    user-defined templates, and then falls back to the defined internal ones.
    """
    loaders = [
        FileSystemLoader([custom_path]),
        PackageLoader("mailbundle.assets", package_path="templates"),
    ]
    env = Environment(loader=ChoiceLoader(loaders))

    return prepare_env(env)


def iter_templates(
    basepath: T.Text, custom_path: T.Text, env: Environment
) -> T.Generator[T.Tuple[T.Text, Template], None, None]:
    """
    Yields all the templates in the environment
    """
    for t in env.list_templates(extensions="jinja"):
        tmpl = env.get_template(t)
        filepath = ""
        if tmpl.filename is not None:
            path, filename = os.path.split(tmpl.filename)
            filename = filename.removesuffix(".jinja")
            path = path.removesuffix(DEFAULT_TEMPLATES_REL_PATH)
            filepath = os.path.join(basepath, filename)
        else:
            filepath = os.path.join(basepath, DEFAULT_TEMPLATES_PATH[t])

        yield filepath, tmpl
