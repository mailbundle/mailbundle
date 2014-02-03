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

from jinja2 import Template


def jinja_read(buf, variables):
    tmpl = Template(buf.read())
    return tmpl.render(**variables)


def read_conf():
    # TODO: make it an hook
    from variables import add_variables
    return add_variables()

variables = {}
variables['confdir'] = os.path.realpath('../config/')
variables['outdir'] = os.path.realpath('../config/')
variables['maildir'] = os.path.realpath('../mail/')
variables['mutt_theme'] = 'zenburn'
variables.update(read_conf())

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
            out.write(processed)
            log.info("%s processed" % fname)
