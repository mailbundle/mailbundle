# -*- encoding: utf-8 -*-
import imaplib
import smtplib
import typing as T


KNOWN_ENDPOINTS = {
    # https://developers.google.com/gmail/imap/imap-smtp
    "gmail": {
        "imap": "imap.gmail.com",
        "smtp": "smtp.gmail.com"
    },
    # https://support.microsoft.com/en-us/office/pop-imap-and-smtp-settings-8361e398-8af4-4e97-b147-6c6c4ac95353
    "microsoft": {
        "imap": "outlook.office365.com",
        "smtp": "smtp.office365.com",
    },
    "msn": {
        "imap": "imap-mail.outlook.com",
        "smtp": "smtp-mail.outlook.com",
    },
    # https://support.apple.com/en-us/HT202304
    "icloud": {
        "imap": "imap.mail.me.com",
        "smtp": "smtp.mail.me.com",
    },
    # https://help.yahoo.com/kb/SLN4075.html
    "yahoo": {
        "imap": "imap.mail.yahoo.com",
        "smtp": "smtp.mail.yahoo.com",
    },
    # https://www.autistici.org/docs/mail/connectionparms
    "autistici": {
        "imap": "mail.autistici.org",
        "smtp": "smtp.autistici.org",
    },
    # https://riseup.net/en/email/clients
    "riseup": {
        "imap": "mail.riseup.net",
        "smtp": "mail.riseup.net",
    },
}
DOMAIN_MAP = {
    # gmail
    "gmail.com": "gmail",
    # microsoft
    "msn.com": "msn",
    "live.com": "microsoft",
    "live.at": "microsoft",
    "live.ca": "microsoft",
    "outlook.com": "microsoft",
    "hotmail.com": "microsoft",
    "hotmail.de": "microsoft",
    "hotmail.at": "microsoft",
    "hotmail.bs": "microsoft",
    "hotmail.ca": "microsoft",
    "hotmail.co.li": "microsoft",
    "hotmail.com.ar": "microsoft",
    "hotmail.com.au": "microsoft",
    "hotmail.com.br": "microsoft",
    "hotmail.com.tr": "microsoft",
    "hotmail.co.uk": "microsoft",
    "hotmail.dk": "microsoft",
    "hotmail.es": "microsoft",
    "hotmail.fr": "microsoft",
    "hotmail.it": "microsoft",
    "hotmail.se": "microsoft",
    "windowslive.com": "microsoft",
    # apple
    "icloud.com": "icloud",
    # yahoo
    "yahoo.com": "yahoo",
    # riseup
    "riseup.net": "riseup",
    # A/I
    "logorroici.org": "autistici",
    "hacari.net": "autistici",
    "mortemale.org": "autistici",
    "canaglie.net": "autistici",
    "hacari.org": "autistici",
    "insicuri.net": "autistici",
    "hacari.com": "autistici",
    "privacyrequired.com": "autistici",
    "stronzi.org": "autistici",
    "subvertising.org": "autistici",
    "distruzione.org": "autistici",
    "onenetbeyond.org": "autistici",
    "canaglie.org": "autistici",
    "bruttocarattere.org": "autistici",
    "autoproduzioni.net": "autistici",
    "grrlz.net": "autistici",
    "bastardi.net": "autistici",
    "autistiche.org": "autistici",
    "paranoici.org": "autistici",
    "krutt.org": "autistici",
    "insiberia.net": "autistici",
    "cryptolab.net": "autistici",
    "anche.no": "autistici",
    "inventati.org": "autistici",
    "autistici.org": "autistici",
}


IMAP_SUBDOMAINS = ["imap", "mail", "imap.mail"]
SMTP_SUBDOMAINS = ["smtp", "mail", "smtp.mail"]
TIMEOUT = 2


def resolve_endpoints(email: T.Text) -> T.Tuple[T.Optional[T.Text], T.Optional[T.Text]]:
    """
    This function tries to resolve the IMAP and SMTP endpoints
    for the given email address.
    """
    domain = email.split("@")[1]

    # Try with known domains
    known_domain = DOMAIN_MAP.get(domain)
    if known_domain:
        return (
            KNOWN_ENDPOINTS[known_domain]["imap"],
            KNOWN_ENDPOINTS[known_domain]["smtp"],
        )

    # Try to guess the domain
    imap, smtp = try_domain(domain)
    if not (imap is None or smtp is None):
        return imap, smtp

    # Try using the mx record
    import dns.resolver

    answers = dns.resolver.resolve(domain, "MX")
    for rdata in answers:
        domain_obj = None
        import ipdb
        ipdb.set_trace()

        # may be a list for multiple mx records or a single result
        if isinstance(rdata.exchange, list):
            if rdata.exchange:
                domain_obj = rdata.exchange[0]
        else:
            domain_obj = rdata.exchange

        if domain_obj:
            # the last slicing is to remove the last "." from domain resolution
            domain = domain_obj.to_text()
            domain = domain[:len(domain)-1]
            break

    if domain:
        imap, smtp = try_domain(domain)
        if not (imap is None or smtp is None):
            return imap, smtp

    return None, None


def try_domain(domain: T.Text) -> T.Tuple[T.Optional[T.Text], T.Optional[T.Text]]:
    imap = None
    smtp = None

    for sub in IMAP_SUBDOMAINS:
        if try_imap_host(f"{sub}.{domain}"):
            imap = f"{sub}.{domain}"
            break

    if try_imap_host(domain):
        imap = domain

    for sub in SMTP_SUBDOMAINS:
        if try_smtp_host(f"{sub}.{domain}"):
            smtp = f"{sub}.{domain}"
            break

    if try_smtp_host(domain):
        imap = domain

    return imap, smtp


def try_imap_host(host: T.Text) -> bool:
    try:
        with imaplib.IMAP4(host, timeout=TIMEOUT) as M:
            M.noop()
        return True
    except (imaplib.IMAP4.error, ConnectionError, TimeoutError):
        pass

    try:
        with imaplib.IMAP4_SSL(host, timeout=TIMEOUT) as M:
            M.noop()
        return True
    except (imaplib.IMAP4_SSL.error, ConnectionError, TimeoutError):
        pass

    return False


def try_smtp_host(host: T.Text) -> bool:
    try:
        with smtplib.SMTP(host, timeout=TIMEOUT) as S:
            S.noop()
        return True
    except (smtplib.SMTPException, ConnectionError, TimeoutError):
        pass

    try:
        with smtplib.SMTP_SSL(host, timeout=TIMEOUT) as S:
            S.noop()
        return True
    except (smtplib.SMTPException, ConnectionError, TimeoutError):
        pass

    return False
