#!/usr/bin/env python3
"""
This is the main program you'll need.
It will create a configuration from your sources
"""
import collections
import json
import logging
import os
import shutil
import stat
import subprocess

from jinja2 import Environment, FileSystemLoader, contextfilter

import gpgvalid

logging.basicConfig(level=logging.INFO)
os.chdir(os.path.dirname(__file__))
log = logging.getLogger("main")

jinja_env = Environment(loader=FileSystemLoader(["custom_templates", "templates"]))
jinja_env.globals["gpg_valid"] = gpgvalid.valid_emails


def avail_bin(progname):
    try:
        devnull = open("/dev/null", "w")
        subprocess.check_call(["which", progname], stdout=devnull, stderr=devnull)
        return True
    except subprocess.CalledProcessError:
        return False


def first_avail_bin(prognames, message=None):
    for progname in prognames:
        if avail_bin(progname):
            return progname
    if message is not None:
        log.warning(message)
    return False


def mkpath(path):
    """same as mkdir -p"""
    # FIXME: completely wrong
    if not os.path.exists(path):
        os.mkdir(path)
        os.chmod(path, stat.S_IRWXU)
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)


def find(basedir):
    """find ${basedir}"""

    def rel(path):
        return os.path.relpath(path, basedir)

    for root, dirs, filenames in os.walk(basedir):
        yield rel(root) + os.path.sep
        for fname in filenames:
            yield rel(os.path.join(root, fname))


# Jinja {{{2
@contextfilter
def warn(ctx, s):
    logging.getLogger("templates.%s" % ctx.name.split(".")[0]).warning(s)
    return ""


@contextfilter
def info(ctx, s):
    logging.getLogger("templates.%s" % ctx.name.split(".")[0]).info(s)
    return ""


@contextfilter
def debug(ctx, s):
    logging.getLogger("templates.%s" % ctx.name.split(".")[0]).debug(s)
    return ""


jinja_env.filters["warn"] = warn
jinja_env.filters["info"] = info
jinja_env.filters["debug"] = debug
jinja_env.tests["avail_bin"] = avail_bin


def jinja_read(fname, variables):
    """take a buffer, context variables, and produce a string"""
    with open(fname) as buf:
        content = buf.read()
        tmpl = jinja_env.from_string(content)
    return tmpl.render(**variables)


# Jinja }}}2


# Configuration {{{2
def check_ext(filename):
    """
    check if the filename ends with one of the supported formats
    (json, yml, yaml, toml)
    """
    if any(filename.endswith(ext) for ext in (".json", ".yml", ".yaml", ".toml")):
        return True
    return False


def get_conf_files():
    """
    get configuration files, sorted and filtered
    """
    files = sorted(
        f for f in os.listdir("vars") if check_ext(f) and not f.startswith(".")
    )
    files_no_ext = [f.rsplit(".", 1)[0] for f in files]
    count_files = collections.Counter(f for f in files_no_ext)
    for fname, fcount in count_files.items():
        if fcount != 1:
            log.error(
                "The same filename %r is present with many extensions. "
                "Maybe you want to choose only one of them." % fname
            )
            raise ValueError
    for fname in files:
        if not fname[:2].isdigit():
            log.warning("Configuration file %s does not follow sorting convention" % fname)
    return files


def read_conf():
    """
    read configuration in vars/
    """
    variables = {}
    files = get_conf_files()
    log.debug("confs: %r" % ",".join(files))
    for fname in files:
        with open(os.path.join("vars", fname)) as buf:
            if fname.endswith(".json"):
                variables.update(json.load(buf))
            if fname.endswith(".yaml") or fname.endswith(".yml"):
                import yaml

                variables.update(yaml.safe_load(buf))
            if fname.endswith(".toml"):
                import toml

                variables.update(toml.load(buf))
    return variables


def read_pyconf():
    """
    read configuration in variables.py.
    Intended for hacks that need a programming language
    """
    return {}


def get_conf():
    """
    get configuration merging defaults, src/vars/ directory and variables.py
    """
    variables = {}
    variables["confdir"] = os.path.realpath("../config/")
    variables["outdir"] = os.path.realpath("../config/")
    variables["maildir"] = os.path.realpath("../mail/")
    variables["mutt_theme"] = "zenburn"

    variables.update(read_conf())
    variables.setdefault("programs", {})
    variables.setdefault("compose", {})
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
    variables["sidebar"].setdefault(
        "additional_tags", notmuch_tags_in_sidebar(variables)
    )
    variables["sidebar"].setdefault("tagsQuery", "date:1w.. and not tag:encrypted and tag:lists")
    variables["notmuch"] = {"all_tags": all_notmuch_tags()}
    variables.update(read_pyconf())
    for account in variables["accounts"]:
        passfile = os.path.join("static", "password", account["name"])
        account.setdefault("fetch", True)
        if not os.path.exists(passfile):
            log.warning(
                "Account %s doesn't have its password; set it on %s"
                % (account["name"], passfile)
            )
    return variables


# End configuration }}}2


# Notmuch {{{2
def all_notmuch_tags(query="*"):
    if os.path.isdir("../mail/") and os.path.isdir("../mail/.notmuch/"):
        p = subprocess.Popen(
            ["notmuch", "search", "--output=tags", query],
            env=dict(NOTMUCH_CONFIG=os.path.normpath("../config/notmuch-config")),
            stdout=subprocess.PIPE,
        )
        out, err = p.communicate()
        out = out.decode("utf8")
        return out.split("\n")
    return []

def all_notmuch_tags_repeated(query="*"):
    if not (os.path.isdir("../mail/") and os.path.isdir("../mail/.notmuch/")):
        return []

    p = subprocess.Popen(
        ["notmuch", "search", "--output=summary" , "--format=json", query],
        env=dict(NOTMUCH_CONFIG=os.path.normpath("../config/notmuch-config")),
        stdout=subprocess.PIPE,
    )
    out, err = p.communicate()
    data = json.loads(out.decode('utf8'))

    for message in data:
        for tag in message.get('tags', []):
            yield tag


def notmuch_tags_in_sidebar(variables):
    query = variables["sidebar"]["tagsQuery"]
    if not query:
        query = variables["search"]["defaultPeriod"]
    def ok_tag(tag: str) -> bool:
        if not tag.startswith("lists/"):
            return False
        # In my experience, lists with numeric names are newsletters
        if tag.split('/', 1)[1].isdigit():
            return False
        return True
    c = collections.Counter(t for t in all_notmuch_tags_repeated(query) if ok_tag(t))
    return [tag for tag, n_occurrences in c.most_common(10)]


# End Notmuch }}}2


if __name__ == "__main__":
    variables = get_conf()
    outdir = variables["outdir"]
    mkpath(outdir)

    with open(os.path.join(outdir, "mailbundle.json"), "w") as buf:
        json.dump(variables, buf, indent=2)
    os.chmod(os.path.join(outdir, "mailbundle.json"), 0o600)
    for obj in find("static"):
        dst = os.path.join(outdir, obj)
        if obj.endswith(os.path.sep):
            mkpath(dst)
        else:
            src = os.path.join("static", obj)
            shutil.copy(src, dst)
            if os.access(src, os.X_OK):
                os.chmod(dst, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            else:
                os.chmod(dst, 0o600)

    for obj in find("jinja"):
        dst = os.path.join(outdir, obj)
        if obj.endswith(os.path.sep):
            mkpath(dst)
        elif obj.endswith(".jinja"):
            fname = os.path.join("jinja", obj)
            dst = os.path.join(outdir, obj[:-6])
            processed = jinja_read(fname, variables)
            if os.path.exists(dst) and processed == open(dst, "r").read():
                log.debug("%s not changed" % obj)
            else:
                with open(dst, "w") as out:
                    out.write(processed)
                    log.info("%s updated" % obj)

            if os.access(fname, os.X_OK):
                os.chmod(dst, 0o700)
            else:
                os.chmod(dst, 0o600)
