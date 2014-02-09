Mail Bundle
============

Mail bundle tries to solve the following problems:
* configuring email in the unix way (many small programs) **quickly**
* making your mail easily **movable** between computers and directories
* clearly *distinguish* configuration of software from personal data

In doing this, it resembles a "site compiler" in that it uses jinja templates
that produce the actual configuration (except that it does not produce a
website, but configuration files, obviously)

It also resembles `virtualenv`, giving you the possibility of "entering" an
environment where your mail commands (mutt, offlineimap, notmuch, alot, msmtp)
take configuration from your mail bundle.

Enought talking, let's have a walkthrough.

Quick start
-------------

1.  clone this repo

    ```sh
    git clone https://github.com/boyska/mailbundle
    ```

2.  customize your accounts

    ```sh
    cd src
    cp vars/{0,1}0-accounts.json
    vim vars/10-accounts.json
    ```

3.  Compile the configuration
    
    ```sh
    python buildconf.py
    ```
4.  Enter the environment

    ```sh
    source ../config/activate
    ```

ok, now you are inside the environment. Let's download your mail:
```sh
offlineimap
```

browse it
```sh
mutt
```

(that is, you're done)


Customize your configuration
----------------------------

* file from `jinja/` will be substituted and copied to `config`
* file from `templates/` are read, and can be included from `jinja/`. Think of
  it as a "library"
* file from `static/` are copied, without any templating engine

When you change your configuration, you tipically change something in `jinja/`
or `static/`. Sometimes you could need bigger changes, thus the right solution
is create a new file in `templates/` and use that in `jinja/`.
Remember that jinja is a powerful language: it supports variables, loops,
conditionals, macros, blocks, filter... This means that you can override a part
of the configuration very easily


Dependencies
------------

mailbundle itself has just 2 dependencies: `python2` and `jinja`.
Of course you need the most common mail tools installed:
* offlineimap
* msmtp

Also, you could benefit alot from
* `notmuch` - to index your mail
* `afew` (which depends on notmuch) - to enhance notmuch with intelligent tagging

A MUA is needed; you can choose between
* `mutt`
* `alot`
mutt can be enhanced with several cool patchsets; we especially recommend
`mutt-kz`, which is a fork that integrates with notmuch.

vim: set ts=2 sw=2 tw=79 et:
