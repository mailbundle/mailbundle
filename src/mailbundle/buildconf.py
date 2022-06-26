# -*- encoding: utf-8 -*-
"""
This is the main program you'll need.
It will create a configuration from your sources
"""
import collections
import importlib.abc
import importlib.resources
import logging
import json
import os
import pathlib
import shutil
import stat
import typing as T


from mailbundle import jinja_utils
from mailbundle import notmuch_utils
from mailbundle import prompt
from mailbundle.utils.atomic_fs import atomic_fs


log = logging.getLogger("main")


MAILBUNDLE_DIR_STRUCTURE = {
    "var": {"mail": None, "lib": None},
    "settings": {"vars": None, "overrides": None},
    "environment": None,
}

# The syntax is link_path: target_path
MAILBUNDLE_SYMLINKS = {
    "hooks/on-sent-mail/50-update-count": "../after-getmail/50-update-count",
}


def first_avail_bin(
    prognames: T.Iterable[T.Text], message: T.Optional[T.Text] = None
) -> T.Optional[T.Text]:
    """Given a list of programs, returns the first found in $PATH"""
    for progname in prognames:
        if shutil.which(progname):
            return progname
    if message is not None:
        log.warning(message)
    return None


# https://stackoverflow.com/a/600612
def mkpath(path: T.Text) -> None:
    """same as mkdir -p"""
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)


def find(basedir):
    """find ${basedir}"""

    def rel(path: str):
        return os.path.relpath(path, basedir)

    for root, _, filenames in os.walk(basedir):
        yield rel(root) + os.path.sep
        for fname in filenames:
            yield rel(os.path.join(root, fname))


def flatten(root: T.Text) -> T.List[T.Text]:
    result: T.List[T.Text] = []

    def walk(parent: T.Text, children: T.Dict[T.Text, T.Any]) -> None:
        for path, sub in children.items():
            node = os.path.join(parent, path)
            result.append(node)
            if sub is not None:
                walk(node, sub)

    walk(root, MAILBUNDLE_DIR_STRUCTURE)

    return result


def check_ext(filename):
    """
    check if the filename ends with one of the supported formats
    (json, yml, yaml, toml)
    """
    if any(filename.endswith(ext) for ext in (".json", ".yml", ".yaml", ".toml")):
        return True
    return False


def get_conf_files(vars_path: T.Text) -> T.List[T.Text]:
    """
    get configuration files, sorted and filtered
    """
    files = sorted(
        f for f in os.listdir(vars_path) if check_ext(f) and not f.startswith(".")
    )
    files_no_ext = [f.rsplit(".", 1)[0] for f in files]
    count_files = collections.Counter(f for f in files_no_ext)
    for fname, fcount in count_files.items():
        if fcount != 1:
            log.error(
                "The same filename %r is present with many extensions. "
                "Maybe you want to choose only one of them.", fname
            )
            raise ValueError
    for fname in files:
        if not fname[:2].isdigit():
            log.warning(
                "Configuration file %s does not follow sorting convention", fname
            )
    return files


def read_conf_files(files: T.List[T.Text], vars_path: T.Text) -> T.Dict[T.Text, T.Any]:
    variables: T.Dict[T.Text, T.Any] = {}
    for fname in files:
        with open(os.path.join(vars_path, fname)) as buf:
            if fname.endswith(".json"):
                variables.update(json.load(buf))
            if fname.endswith(".yaml") or fname.endswith(".yml"):
                import yaml

                variables.update(yaml.safe_load(buf))
            if fname.endswith(".toml"):
                import toml

                variables.update(toml.load(buf))

    return variables


def read_conf(vars_path: T.Text) -> T.Dict[T.Text, T.Any]:
    """
    read configuration in vars/
    """
    files = get_conf_files(vars_path)
    if files:
        log.debug("confs: %r", ",".join(files))
        return read_conf_files(files, vars_path)
    else:
        return prompt.ask_variables()


def read_pyconf():
    """
    read configuration in variables.py.
    Intended for hacks that need a programming language
    """
    return {}


def get_conf(basepath: T.Text, vars_path: T.Text) -> T.Dict[T.Text, T.Any]:
    """
    get configuration merging defaults, vars/ directory and variables.py
    """
    variables = {}
    variables["confdir"] = os.path.realpath(os.path.join(basepath, "environment"))
    variables["outdir"] = os.path.realpath(os.path.join(basepath, "environment"))
    variables["maildir"] = os.path.realpath(os.path.join(basepath, "mail"))
    variables["mutt_theme"] = "zenburn"
    variables["use_offlineimap"] = True

    variables.update(read_conf(vars_path))
    variables.setdefault("groups", {})
    variables.setdefault("programs", {})
    variables.setdefault("search", {"defaultPeriod": "1M", "queryAppend": {}})
    variables.setdefault("compose", {})
    variables.setdefault("sidebar", {"tagsEntry": True, "tagsQuery": "*"})
    variables.setdefault("main_account", None)
    variables.setdefault("accounts", [])
    variables["compose"].setdefault("attachment", {})
    variables["compose"]["attachment"].setdefault("words", [])
    variables["programs"].setdefault(
        "url_helper", first_avail_bin(("urlview", "urlscan"), "You have no urlopener")
    )
    variables["programs"].setdefault(
        "sslconnect", first_avail_bin(("socat2", "socat", "openssl"))
    )
    variables["programs"].setdefault(
        "fuzzyfinder", first_avail_bin(("fzy", "fzf", "pick"))
    )
    variables["programs"].setdefault("firejail", first_avail_bin(["firejail"]))
    variables["programs"]["firejail_wrap"] = (
        "%s --dbus-system=none --dbus-user=none --x11=none --net=none --private"
        % variables["programs"]["firejail"]
        if variables["programs"]["firejail"]
        else ""
    )
    variables["sidebar"].setdefault(
        "additional_tags", notmuch_utils.tags_in_sidebar(basepath, variables)
    )
    variables["sidebar"].setdefault(
        "tagsQuery", "date:1w.. and not tag:encrypted and tag:lists"
    )
    variables["sidebar"].setdefault("additionalQueries", {})
    variables["notmuch"] = {"all_tags": notmuch_utils.all_tags(basepath)}
    variables.update(read_pyconf())
    for account in variables["accounts"]:
        passfile = os.path.join("static", "password", account["name"])
        account.setdefault("fetch", True)
        if not os.path.exists(passfile) and not account["password_exec"]:
            log.warning(
                "Account %s doesn't have its password; set it on %s",
                (account["name"], passfile)
            )
    return variables


def render_templates(
    basepath: T.Text, custom_path: T.Text, variables: T.Dict[T.Text, T.Any]
) -> None:
    """
    Renders the templates in the right destinations, creating the parent directories,
    if needed
    """
    env = jinja_utils.get_jinja_env(custom_path)

    for path, tmpl in jinja_utils.iter_templates(basepath, custom_path, env):
        content = tmpl.render(**variables)

        base = os.path.dirname(path)
        if not os.path.isdir(base):
            mkpath(base)

        if os.path.isfile(path):
            with open(path) as conf:
                if conf == content:
                    log.debug("content not changed: %s", path)
                    continue

        with open(path, "w+") as dest:
            dest.write(content)
            log.debug("updated: %s", path)


def iter_package_assets(
    basepath: T.Text, traversable: importlib.abc.Traversable
) -> None:
    for f in traversable.iterdir():
        if f.is_file():
            if f.name == "__init__.py":
                continue
            # No need to try to decode the content
            content = f.read_bytes()
            dst_path = os.path.join(basepath, f.name)
            with open(dst_path, "wb+") as dest:
                dest.write(content)
            os.chmod(dst_path, 0o600)  # TODO: check if this is correct
        elif f.is_dir():
            mkpath(os.path.join(basepath, f.name))
            iter_package_assets(os.path.join(basepath, f.name), f)


def bind_symlinks(basepath: T.Text) -> None:
    for path, tgt in MAILBUNDLE_SYMLINKS.items():
        path = os.path.realpath(os.path.join(basepath, path))
        if tgt.startswith("../"):
            base = os.path.dirname(path)
            tgt = os.path.realpath(os.path.join(base, tgt))
        else:
            tgt = os.path.realpath(os.path.join(basepath, tgt))

        os.symlink(tgt, path)


def iter_custom_assets(outdir: T.Text, custom_path: T.Text) -> None:
    for filepath in find(custom_path):
        if filepath == "." + os.path.sep:
            continue
        if os.path.isfile(filepath):
            src = os.path.join(custom_path, filepath)
            dst = os.path.join(outdir, filepath)
            shutil.copy(src, dst)
            if os.access(src, os.X_OK):
                os.chmod(dst, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            else:
                os.chmod(dst, 0o600)
        elif os.path.isdir(filepath):
            mkpath(os.path.join(outdir, filepath))
            iter_custom_assets(outdir, os.path.join(custom_path, filepath))


def create_static_assets(outdir: T.Text, custom_path: T.Text) -> None:
    files = importlib.resources.files("mailbundle.assets.static")
    iter_package_assets(outdir, files)
    bind_symlinks(outdir)
    iter_custom_assets(outdir, custom_path)


def copy_dir(src: T.Text, dst: T.Text) -> None:
    if src == dst:
        return None
    shutil.copytree(src, dst, dirs_exist_ok=True)


def bootstrap(
    basepath: T.Text,
    vars_path: T.Optional[T.Text],
    overrides_path: T.Optional[T.Text],
) -> None:
    """
    Initializes a mailbundle from configs
    """
    mkpath(basepath)

    dst_vars = os.path.join(basepath, "settings", "vars")
    dst_overrides = os.path.join(basepath, "settings", "overrides")

    if vars_path is None:
        vars_path = dst_vars
        mkpath(vars_path)

    if overrides_path is None:
        overrides_path = dst_overrides
        mkpath(overrides_path)

    # TODO: we need to provide here the values from outside! (or silence the errors)
    variables = get_conf(basepath, vars_path)

    bundle_path = variables["outdir"]

    for path in flatten(basepath):
        mkpath(path)

    # write the resulting variables to mailbundle.json
    with open(os.path.join(basepath, "mailbundle.json"), "w+") as buf:
        json.dump(variables, buf, indent=2)
    os.chmod(os.path.join(basepath, "mailbundle.json"), 0o600)

    with atomic_fs(bundle_path) as tmp_path:
        create_static_assets(tmp_path, overrides_path)
        render_templates(tmp_path, overrides_path, variables)
        copy_dir(vars_path, dst_vars)
        copy_dir(overrides_path, dst_overrides)
