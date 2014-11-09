#!/usr/bin/env bash

base=$(dirname $0)
ve="$base/dep/ve"
py="${ve}/bin/python"
pip="${ve}/bin/pip"
cd "$base"
git submodule init
git submodule update
virtualenv2 --no-site-packages "$ve"
"${py}" dep/afew/setup.py install
"${pip}" install -r src/requirements.txt

