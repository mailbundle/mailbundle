Quickstart
==============

Installation of external software
---------------------------------

Mailbundle assumes lot of things about your system and your mail usage.
It relies on recent version (as of 2016) of software and sometimes even
patched ones. One particularly important "dependency" is ``mutt-kz``, which is
a version of mutt patched for built-in notmuch support. ``mutt-kz`` is not packaged in debian repositories, but compiling it should be easy. It is available in Archlinux AUR.

Many other external softwares can be installed/compiled using the scripts ``debian-deps``/``archlinux-deps`` and ``build-dep``

However, this scripts are still a bit limited, and might _not_ install everything that's needed (or useful!) for mailbundle to work well.

Running mailbundle
------------------

Mailbundle is basically a configuration compiler. So just ``cd src`` and ``./buildconf.py`` should be enough for it to work. It will build a configuration in the ``config/`` directory, but of course it would be a pointless one since you still haven't entered your personal mail details.

Basic configuration
~~~~~~~~~~~~~~~~~~~

Configuration is handled in ``src/vars/``. You will find some skeleton files containing the defaults. Don't remove them, there's no need to. The best thing to do is copying them with a higher number. Mailbundle will merge all the files in that directory in ascending order, so copying a file and changing some details is the best way to "override".

``accounts`` is a list of... accounts. starting from the default it should be quite intuitive to get your account ready. Some of those fields are, however, not really intuitive. ``smtp_fingerprint`` is the fingerprint of the SSL certificate of the SMTP server. Similarly, ``imap_fingerprint`` is the fingerprint of the SSL certificate of the SMTP server. You can get those using ``bin/get_fp``.

Inside the mailbundle
~~~~~~~~~~~~~~~~~~~~~

what mailbundle set up is not some random configuration file, but a coherent
environment in which all mail-related programs are well integrated. You can compare it to a python "virtual environment".
To enter mailbundle, run ``/path/to/mailbundle/config/bin/autorun``.
This will launch tmux with two window open: one is a loop fetching mail, the
other is a ``mutt`` window.
