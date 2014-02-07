'''
This is the main program you'll need.
It will create a configuration from your sources
'''
import os
from glob import iglob
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('main')
import shutil
import json

from jinja2 import Template


def jinja_read(buf, variables):
    tmpl = Template(buf.read().decode('utf-8'))
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

outdir = variables['outdir']
if not os.path.exists(outdir):
    os.mkdir(outdir)  # TODO: mkdir -p

for obj in os.listdir('static'):
    path = os.path.join('static', obj)
    if os.path.isdir(path):
        try:
            # FIXME: error if directory already exists
            # shall we delete it? shall we just "rsync"?
            shutil.copytree(path, os.path.join(outdir, obj))
        except:
            logging.exception("uff, copytree sucks")
    else:
        shutil.copy(path, outdir)

for fname in iglob('*.jinja'):
    with open(fname) as src:
        processed = jinja_read(src, variables)
        # TODO: strip extension
        with open(os.path.join(outdir, fname[:-6]), 'w') as out:
            out.write(processed.encode('utf-8'))
            log.info("%s processed" % fname)
