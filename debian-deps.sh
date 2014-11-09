#!/usr/bin/env bash

PACKAGES="
python2.7
python-jinja2
mutt
notmuch
realpath
offlineimap
msmtp
python-notmuch
dbacl
python-dev
python-setuptools
zsh
"
apt-get install -y $PACKAGES
