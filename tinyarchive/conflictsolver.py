import abc
import logging
import urlparse

import tinyback

class ConflictSolver:

    __metaclass__ = abc.ABCMeta

    def __init__(self, service):
        self._log = logging.getLogger("ConflictSolver%s" % service)

    @abc.abstractmethod
    def solve(self, code, stored_url, url):
        pass

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
                raise ValueError()
        except tinyback.exceptions.NoRedirectException:
            self._log.fatal("Code suddenly disappeared")
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

class BitlyConflictSolver(ConflictSolver):

    def solve(self, code, stored_url, url):
        netloc = urlparse.urlparse(url).netloc
        stored_netloc = urlparse.urlparse(stored_url).netloc
        if stored_netloc.lower() == netloc:
            return stored_url
        raise ValueError("Unsolvable conflict for code %s" % code)

class IsgdConflictSolver(ConflictSolver):

    def solve(self, code, stored_url, url):
        if len(stored_url) > 1000 and stored_url[:1000] == url:
            return stored_url
        raise ValueError("Unsolvable conflict for code %s" % code)

class TinyurlConflictSolver(ConflictSolver):

    def __init__(self, service):
        super(TinyurlConflictSolver, self).__init__(service)
        if service != "tinyurl":
            raise ValueError("TinyurlConflictSolver only works for service tinyurl")
        self._service = None

    def solve(self, code, stored_url, url):
        if url.strip() == stored_url.strip():
            return url

        netloc = urlparse.urlparse(stored_url).netloc
        if netloc in ["clickserve.cc-dt.com", "www.kqzyfj.com", "www.dpbolvw.net", "click.linksynergy.com", "www.anrdoezrs.net", "www.jdoqocy.com", "ticketsuk.at", "www.awin1.com", "send.onenetworkdirect.net", "www.tkqlhce.com", "track.webgains.com"]:
            return url
        for amazon in ["amazon.com", "amazon.ca", "amazon.co.uk", "amazon.de", "amazon.fr"]:
            if netloc.endswith(amazon) and "tag=" in stored_url and not "tag=" in url:
                return url

        if url.decode("ascii", "ignore") == stored_url.decode("ascii", "ignore"):
            if not self._service:
                self._service = tinyback.services.factory("tinyurl")
            if self._service.fetch(code) == url:
                return url

        raise ValueError("Unsolvable conflict for code %s" % code)

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
