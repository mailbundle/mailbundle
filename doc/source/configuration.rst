Configuration details
=====================

This page describe the possible variables

Account
-------

``accounts`` is a list of "objects". Any object describe an Account, and can have the following values:

imap_fingerprint
  fingerprint of the SSL certificate of the IMAP server
smtp_fingerprint
  fingerprint of the SSL certificate of the SMTP server
torify
  takes a boolean and connects through Tor. Please note that certificate verification is _different_ when using Tor.

Groups
--------

pgp_validity
  this option will create a group based on the gpg-validity of at least one key that belongs to the email. Its value is  one of ``unknown``, ``marginal``, ``full``, ``ultimate``. It means that it is the _minimum_ validity. Therefore setting it to ``unknown`` matches everything, while setting it to ``ultimate`` only matches your own key.
to_domains
  this will match an email based on the domain. It is a list of regexp, so ``.*\.gov`` can be used.
  Examples:

  - ``["gmail.com", "hotmail.com", ".*\.tk"]``
  - ``[".*\.edu", "ethz\.ch"]``
to
  list of emails. Those are not regexp, so you must write them exactly.
  Example: ``["joe@avera.ge", "mallory@malicious"]``
  

Hooks
---------
