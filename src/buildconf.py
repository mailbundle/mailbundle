import os
from glob import iglob
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
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
variables.update(read_conf())

outdir = variables['outdir']

for fname in iglob('*.static'):
    shutil.copyfile(fname, os.path.join(outdir, fname[:-7]))
    log.info("%s copied" % fname)

for fname in iglob('*.jinja'):
    with open(fname) as src:
        processed = jinja_read(src, variables)
        # TODO: strip extension
        with open(os.path.join(outdir, fname[:-6]), 'w') as out:
            out.write(processed)
            log.info("%s processed" % fname)
