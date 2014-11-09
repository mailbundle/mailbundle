#!/usr/bin/env bash

base=$(realpath $(dirname $0))
ve="$base/dep/ve2"
vethree="$base/dep/ve3"
py="${ve}/bin/python"
pythree="${vethree}/bin/python"
pipthree="${vethree}/bin/pip"
pip="${ve}/bin/pip"
cd "$base"
git submodule init
git submodule update
virtualenv2 --no-site-packages "$ve"
virtualenv3 --no-site-packages "$vethree"
cd "dep/afew"
"${pythree}" setup.py install
cd "$base"
"${pip}" install -r src/requirements.txt

