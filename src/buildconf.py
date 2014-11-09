#!/usr/bin/env python2.7
'''
This is the main program you'll need.
It will create a configuration from your sources
'''
import os
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('main')
import shutil
import json
import subprocess

from jinja2 import Environment, FileSystemLoader

import gpgvalid
jinja_env = Environment(loader=FileSystemLoader(['custom_templates',
                                                 'templates']))
jinja_env.globals['gpg_valid'] = gpgvalid.valid_emails


def jinja_read(fname, variables):
    '''take a buffer, context variables, and produce a string'''
    with open(fname) as buf:
        content = buf.read().decode('utf-8')
        tmpl = jinja_env.from_string(content)
    return tmpl.render(**variables)


def read_jsonconf():
    '''
    read configuration in vars/
    '''
    variables = {}
    for fname in sorted(os.listdir('vars')):
        if not fname.endswith('.json'):
            continue
        if not fname[:2].isdigit():
            log.warn("Configuration file %s does not follow sorting convention"
                     % fname)
        with open(os.path.join('vars', fname)) as buf:
            variables.update(json.load(buf))
    return variables


def read_pyconf():
    '''
    read configuration in variables.py.
    Intended for hacks that need a programming language
    '''
    return {}


variables = {}
variables['confdir'] = os.path.realpath('../config/')
variables['outdir'] = os.path.realpath('../config/')
variables['maildir'] = os.path.realpath('../mail/')
variables['mutt_theme'] = 'zenburn'

# TODO: check which executable is available and do a preference list
for helper in ('urlscan', 'urlview'):
    try:
        devnull = open('/dev/null', 'w')
        subprocess.check_call(['which', helper],
                              stdout=devnull, stderr=devnull)
        variables['url_helper'] = helper
    except subprocess.CalledProcessError:
        pass
variables.update(read_jsonconf())
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
    os.chmod(path, 0700)


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

    for obj in find('static'):
        dst = os.path.join(outdir, obj)
        if obj.endswith(os.path.sep):
            mkpath(dst)
        else:
            src = os.path.join('static', obj)
            shutil.copy(src, dst)
            if os.access(src, os.X_OK):
                os.chmod(dst, 0700)
            else:
                os.chmod(dst, 0600)

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
                os.chmod(0700)
            else:
                os.chmod(dst, 0600)
