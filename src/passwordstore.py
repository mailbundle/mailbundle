#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import gnupg

def get_store_path():
    if 'PASSWORD_STORE_DIR' in os.environ:
        dir = os.environ['PASSWORD_STORE_DIR']
    else:
        dir = os.path.expanduser('~') + "/.password-store"
    return dir

def decrypt(path):
    gpg = gnupg.GPG()
    txt = open(get_store_path() + "/" + path + ".gpg", "rb")
    data = gpg.decrypt_file(txt)
    if data.status == "decryption ok":
        content = data.data.decode('utf-8').split("\n")
        dict = {'password': data[0]}
        for item in data[1:]:
            split = item.split(': ')
            dict[split[0]] = split[1]
        return dict
    else:
       raise Exception("Passphrase not supplied!")
