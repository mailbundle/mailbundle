#!/usr/bin/env python2.7
'''
This is the main program you'll need.
It will create a configuration from your sources
'''
import collections
import os
import logging
import stat
import shutil
import json
import subprocess

from jinja2 import Environment, FileSystemLoader, contextfilter

import gpgvalid

logging.basicConfig(level=logging.INFO)
os.chdir(os.path.dirname(__file__))
log = logging.getLogger('main')

jinja_env = Environment(loader=FileSystemLoader(['custom_templates',
                                                 'templates']))
jinja_env.globals['gpg_valid'] = gpgvalid.valid_emails


def avail_bin(progname):
    try:
        devnull = open('/dev/null', 'w')
        subprocess.check_call(['which', progname],
                              stdout=devnull, stderr=devnull)
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


@contextfilter
def warn(ctx, s):
    logging.getLogger('templates.%s' % ctx.name.split('.')[0]).warn(s)
    return ''


@contextfilter
def info(ctx, s):
    logging.getLogger('templates.%s' % ctx.name.split('.')[0]).info(s)
    return ''


@contextfilter
def debug(ctx, s):
    logging.getLogger('templates.%s' % ctx.name.split('.')[0]).debug(s)
    return ''


jinja_env.filters['warn'] = warn
jinja_env.filters['info'] = info
jinja_env.filters['debug'] = debug
jinja_env.tests['avail_bin'] = avail_bin


def jinja_read(fname, variables):
    '''take a buffer, context variables, and produce a string'''
    with open(fname) as buf:
        content = buf.read().decode('utf-8')
        tmpl = jinja_env.from_string(content)
    return tmpl.render(**variables)


def check_ext(filename):
    '''
    check if the filename ends with one of the supported formats
    (json, yml, yaml, toml)
    '''
    fext = lambda ext: filename.endswith(ext)
    if any(fext(ext) for ext in ('.json', '.yml', '.yaml', '.toml')):
        return True
    return False


def get_conf_files():
    '''
    get configuration files, sorted and filtered
    '''
    files = sorted(f for f in os.listdir('vars')
                   if check_ext(f) and not f.startswith('.'))
    files_no_ext = [f.rsplit('.', 1)[0] for f in files]
    count_files = collections.Counter(f for f in files_no_ext)
    for fname, fcount in count_files.items():
        if fcount != 1:
            log.error("The same filename %r is present with many extensions. "
                      "Maybe you want to choose only one of them." % fname)
            raise ValueError
    for fname in files:
        if not fname[:2].isdigit():
            log.warn("Configuration file %s does not follow sorting convention"
                     % fname)
    return files


def read_conf():
    '''
    read configuration in vars/
    '''
    variables = {}
    files = get_conf_files()
    log.debug("confs: %r" % ','.join(files))
    for fname in files:
        with open(os.path.join('vars', fname)) as buf:
            if fname.endswith('.json'):
                variables.update(json.load(buf))
            if fname.endswith('.yaml') or fname.endswith('.yml'):
                import yaml
                variables.update(yaml.safe_load(buf))
            if fname.endswith('.toml'):
                import toml
                variables.update(toml.load(buf))
    return variables


def read_pyconf():
    '''
    read configuration in variables.py.
    Intended for hacks that need a programming language
    '''
    return {}


def all_notmuch_tags(query='*'):
    if os.path.isdir('../mail/') and os.path.isdir('../mail/.notmuch/'):
        p = subprocess.Popen(
            ['notmuch', 'search', '--output=tags', query],
            env=dict(NOTMUCH_CONFIG=os.path.normpath(
                '../config/notmuch-config')),
            stdout=subprocess.PIPE
        )
        out, err = p.communicate()
        return out.split('\n')
    return []


def notmuch_tags_in_sidebar(variables):
    query = variables['sidebar']['tagsQuery']
    if not query:
        query = variables['search']['defaultPeriod']
    return [t for t in all_notmuch_tags(query) if t.startswith('lists/')]


variables = {}
variables['confdir'] = os.path.realpath('../config/')
variables['outdir'] = os.path.realpath('../config/')
variables['maildir'] = os.path.realpath('../mail/')
variables['mutt_theme'] = 'zenburn'

variables.update(read_conf())
variables.setdefault('programs', {})
variables.setdefault('compose', {})
variables['compose'].setdefault('attachment', {})
variables['compose']['attachment'].setdefault('words', [])
variables['programs'].setdefault('url_helper',
                                 first_avail_bin(('urlview', 'urlscan'),
                                                 "You have no urlopener"))
variables['programs'].setdefault('sslconnect',
                                 first_avail_bin(('socat2',
                                                  'socat',
                                                  'openssl')))
variables['programs'].setdefault('fuzzyfinder',
                                 first_avail_bin(('fzy',
                                                  'fzf',
                                                  'pick')))
variables['sidebar'].setdefault('additional_tags',
                                notmuch_tags_in_sidebar(variables))
variables['sidebar'].setdefault('tagsQuery', '')
variables['notmuch'] = {
    'all_tags': all_notmuch_tags()
}


variables.update(read_pyconf())
for account in variables['accounts']:
    passfile = os.path.join('static', 'password', account['name'])
    if not os.path.exists(passfile):
        log.warn("Account %s doesn't have its password; set it on %s" %
                 (account['name'], passfile))


def mkpath(path):
    '''same as mkdir -p'''
    # FIXME: completely wrong
    if not os.path.exists(path):
        os.mkdir(path)
        os.chmod(path, stat.S_IRWXU)
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)


def find(basedir):
    '''find ${basedir}'''
    def rel(path):
        return os.path.relpath(path, basedir)
    for root, dirs, filenames in os.walk(basedir):
        yield rel(root) + os.path.sep
        for fname in filenames:
            yield rel(os.path.join(root, fname))

outdir = variables['outdir']

if __name__ == '__main__':
    mkpath(outdir)

    with open(os.path.join(outdir, 'mailbundle.json'), 'w') as buf:
        json.dump(variables, buf)
    os.chmod(os.path.join(outdir, 'mailbundle.json'), 0o600)
    for obj in find('static'):
        dst = os.path.join(outdir, obj)
        if obj.endswith(os.path.sep):
            mkpath(dst)
        else:
            src = os.path.join('static', obj)
            shutil.copy(src, dst)
            if os.access(src, os.X_OK):
                os.chmod(dst, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            else:
                os.chmod(dst, 0o600)

    for obj in find('jinja'):
        dst = os.path.join(outdir, obj)
        if obj.endswith(os.path.sep):
            mkpath(dst)
        elif obj.endswith('.jinja'):
            fname = os.path.join('jinja', obj)
            dst = os.path.join(outdir, obj[:-6])
            processed = jinja_read(fname, variables)
            if os.path.exists(dst) and \
                    processed == open(dst, 'r').read().decode('utf-8'):
                log.debug("%s not changed" % obj)
            else:
                with open(dst, 'w') as out:
                    out.write(processed.encode('utf-8'))
                    log.info("%s updated" % obj)

            if os.access(fname, os.X_OK):
                os.chmod(dst, 0o700)
            else:
                os.chmod(dst, 0o600)
