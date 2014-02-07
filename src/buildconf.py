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

from jinja2 import Environment, FileSystemLoader
jinja_env = Environment(loader=FileSystemLoader('templates'))


def jinja_read(buf, variables):
    '''take a buffer, context variables, and produce a string'''
    tmpl = jinja_env.from_string(buf.read().decode('utf-8'))
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
variables.update(read_jsonconf())
variables.update(read_pyconf())


def mkpath(path):
    '''same as mkdir -p'''
    #FIXME: completely wrong
    if not os.path.exists(path):
        os.mkdir(path)


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

    for obj in find('jinja'):
        dst = os.path.join(outdir, obj)
        if obj.endswith(os.path.sep):
            mkpath(dst)
        elif obj.endswith('.jinja'):
            fname = os.path.join('jinja', obj)
            with open(fname) as src:
                processed = jinja_read(src, variables)
                with open(os.path.join(outdir, obj[:-6]), 'w') as out:
                    out.write(processed.encode('utf-8'))
                    log.info("%s processed" % fname)
