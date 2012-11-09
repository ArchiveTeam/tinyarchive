import logging
import urlparse

import tinyback

class ConflictSolver(object):

    def __init__(self, service):
        self._log = logging.getLogger("ConflictSolver.%s" % service)

    def solve(self, code, stored_url, url):
        self._log.fatal("Code %s, stored URL is '%s' but new URL is '%s'" % (code, stored_url.decode("ascii", "ignore"), url.decode("ascii", "ignore")))
        raise ValueError("Unsolvable conflict for code %s" % code)

class AutomaticConflictSolver(ConflictSolver):

    def __init__(self, service):
        super(AutomaticConflictSolver, self).__init__(service)
        self._service = tinyback.services.factory(service)

    def solve(self, code, stored_url, url):
        self._log.info("Refetching URL for code %s" % code)
        try:
            real_url = self._service.fetch(code)
            if real_url == url:
                return url
            else:
                self._log.fatal("Code %s leads to '%s', but stored URL was '%s' and new URL was '%s'" % (code, real_url, stored_url, url))
                raise ValueError("New URL for code %s does not mach real URL" % code)
        except tinyback.exceptions.NoRedirectException:
            self._log.fatal("Code %s suddenly disappeared" % code)
            raise ValueError()

class ManualConflictSolver(AutomaticConflictSolver):

    def solve(self, code, stored_url, url):
        real_url = super(ManualConflictSolver, self).solve(code, stored_url, url)
        print("---------------------------------------------")
        print("(1) Stored URL:  %s" % stored_url)
        print("(2) New URL:     %s" % url)
        print("(3) Real URL:    %s" % real_url)
        while True:
            choice = raw_input("Choice? ").strip()
            if choice == "1":
                return stored_url
            elif choice == "2":
                return url
            elif choice == "3":
                return real_url

class BitlyConflictSolver(ManualConflictSolver):

    def solve(self, code, stored_url, url):
        netloc = urlparse.urlparse(url).netloc
        stored_netloc = urlparse.urlparse(stored_url).netloc
        if stored_netloc.lower() == netloc:
            return stored_url
        if stored_netloc[-1] == ":" and stored_netloc[:-1] == netloc:
            return url
        return super(BitlyConflictSolver, self).solve(code, stored_url, url)

class IsgdConflictSolver(ManualConflictSolver):

    def solve(self, code, stored_url, url):
        if len(stored_url) > 1000 and stored_url[:1000] == url:
            return stored_url
        return super(IsgdConflictSolver, self).solve(code, stored_url, url)

class TinyurlConflictSolver(AutomaticConflictSolver):

    def __init__(self, service):
        super(TinyurlConflictSolver, self).__init__(service)

    def solve(self, code, stored_url, url):
        if url.strip() == stored_url.strip():
            return url

        hostname = urlparse.urlparse(stored_url).hostname
        if hostname in ["www.pntra.com", "scripts.affiliatefuture.com", "www.pjatr.com", "pjtra.com", "clickserve.cc-dt.com", "www.kqzyfj.com", "www.dpbolvw.net", "click.linksynergy.com", "www.anrdoezrs.net", "www.jdoqocy.com", "ticketsuk.at", "www.awin1.com", "send.onenetworkdirect.net", "www.tkqlhce.com", "track.webgains.com", "ticketsus.at"]:
            return url
        for amazon in ["amazon.com", "amazon.ca", "amazon.co.uk", "amazon.de", "amazon.fr"]:
            if hostname.endswith(amazon) and "tag=" in stored_url and not "tag=" in url:
                return url

        if url.decode("ascii", "ignore") == stored_url.decode("ascii", "ignore"):
            self._service = tinyback.services.factory("tinyurl")
            if self._service.fetch(code) == url:
                return url

        return super(TinyurlConflictSolver, self).solve(code, stored_url, url)


def factory(service):
    if service == "bitly":
        solver = BitlyConflictSolver
    elif service == "isgd":
        solver = IsgdConflictSolver
    elif service == "tinyurl":
        solver = TinyurlConflictSolver
    else:
        solver = ManualConflictSolver
    return solver(service)
