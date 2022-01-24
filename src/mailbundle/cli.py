# -*- encoding: utf-8 -*-
import typing as T

import click

from mailbundle.buildconf import bootstrap


@click.group()
@click.option(
    "-C",
    "--config",
    type=click.Path(),
    default=None,
    help="The path to a mailbundler.json config file",
)
@click.pass_context
def main(ctx: click.Context, config: T.Optional[T.Text]) -> None:
    """Main cli entrypoint"""
    if ctx.obj is None:
        ctx.obj = {}
    ctx.obj["config"] = config  # TODO: find default config


@main.command("bootstrap", help="This bootstraps a new mailbundle")
@click.option(
    "-V",
    "--vars",
    type=click.Path(),
    default=None,
    help="Path to variables",
)
@click.option(
    "-o",
    "--overrides",
    type=click.Path(),
    default=None,
    help="Path to custom (user-defined) templates and static assets",
)
@click.argument(
    "destination",
    type=click.Path(),
    nargs=1,
)
@click.pass_context
def bootstrap_cli(
    ctx: click.Context,
    vars: T.Optional[T.Text],
    overrides: T.Optional[T.Text],
    destination: T.Text,
) -> None:
    bootstrap(destination, vars, overrides)
