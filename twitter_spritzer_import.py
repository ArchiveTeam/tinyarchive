#!/usr/bin/env python

# TinyArchive - A tiny web archive
# Copyright (C) 2012 David Triendl
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import re
import sys
import urlparse

import tinyarchive.database

logging.basicConfig(level=logging.DEBUG, format="%(name)s: %(message)s")

db_manager = tinyarchive.database.DBManager(sys.argv[1])

bitly_pro_hosts = ["4ms.me", "4sq.com", "amba.to", "amzn.to", "bbc.in",
    "es.pn", "etsy.me", "glo.bo", "huff.to", "lb.to", "nyti.ms", "on.fb.me",
    "on.mash.to", "on.wsj.com", "reut.rs", "whrt.it", "yhoo.it", "zite.to"]

for line in sys.stdin:
    assert line[-1] == "\n"
    assert line[-2] != "\r"
    if not "|" in line:
        continue

    shorturl, longurl = line[:-1].split("|", 1)
    if not shorturl or not longurl or shorturl == longurl:
        continue

    ps = urlparse.urlparse(shorturl)
    pl = urlparse.urlparse(longurl)

    if not ps.hostname:
        continue

    code = None
    service = None
    verify = False
    if ps.path and ps.path[0] == "/":
        code = ps.path[1:]

    if ps.hostname in bitly_pro_hosts or ps.hostname in ["bit.ly", "j.mp", "bitly.com"]:
        service = "bitly"
        if "/a/warning" in longurl:
            verify = True
    elif ps.hostname == "t.co":
        service = "tco"
    elif ps.hostname == "bit.ly":
        service = "bitly"
    elif ps.hostname == "tmblr.co":
        service = "tmblrco"
    elif ps.hostname == "fb.me":
        service = "fbme"
    elif ps.hostname == "youtu.be":
        service = "youtube"
    elif ps.hostname == "tinyurl.com":
        service = "tinyurl"
    elif ps.hostname == "goo.gl":
        service = "googl"
    elif ps.hostname == "dlvr.it":
        service = "dlvrit"
    elif ps.hostname == "tl.gd":
        service = "tlgd"
    elif ps.hostname in ["ow.ly", "owl.ly", "owl.li"]:
        service = "owly"
    elif ps.hostname == "wl.gs": # Only redirects to post.writelonger.com/CODE
        continue
    elif ps.hostname == "is.gd":
        service = "isgd"
    elif ps.hostname == "vk.cc":
        service = "vkcc"
    elif ps.hostname == "www.youtube.com": # Not a shorturl
        continue
    elif ps.hostname == "tumblr.com": # Not a shorturl
        continue
    elif ps.hostname == "nico.ms": # Only redirects to www.nicovideo.jp/watch/CODE
        continue
    elif ps.hostname == "mtw.tl":
        service = "mtwtl"
    elif ps.hostname == "wp.me":
        service = "wpme"
    elif ps.hostname == "myloc.me": # Only redirects to myloc.me/show.php?id=CODE
        continue
    elif ps.hostname == "tm.to": # Only redirects to twtmore.com/tweet/CODE
        continue
    elif ps.hostname == "dld.bz":
        service = "dldbz"
    elif ps.hostname == "nblo.gs": # Only redirects to networkedblogs.com/CODE
        continue
    elif ps.hostname == "shar.es":
        service = "shares"
    elif ps.hostname == "shrtn.us":
        service = "shrtnus"
    elif ps.hostname == "migre.me":
        service = "migreme"
    elif ps.hostname == "moi.st":
        service = "moist"
    elif ps.hostname == "lnkd.in":
        service = "lnkdin"
    elif ps.hostname == "www.facebook.com": # Not a shorturl
        continue
    elif ps.hostname == "www.stardoll.com": # Not a shorturl
        continue
    elif ps.hostname == "wl.tl": # Only redirects to www.writelonger.com/show/CODE
        continue
    elif ps.hostname == "ask.fm": # Does not appear to work(?)
        continue
    elif ps.hostname == "clck.ru":
        service = "clckru"
    elif ps.hostname == "jdye.info": # Spam domain
        continue
    elif ps.hostname == "ping.fm":
        service = "pingfm"
    elif ps.hostname == "de.tk":
        service = "detk"
    elif ps.hostname == "path.com": # Only redirects from http to https
        continue
    elif ps.hostname == "dw.am": # Only redirects to twtkr.olleh.com/view.php?long_id=CODE
        continue
    elif ps.hostname in ["r10.to", "a.r10.to"]: # URLs are not stable, probably not a shortener(?)
        continue
    elif ps.hostname == "su.pr":
        service = "supr"
    elif ps.hostname == "soc.li": # URLs are not stable, appears to be spam(?)
        continue
    elif ps.hostname == "plurk.com": # Only redirects to www.plurk.com/CODE
        continue
    elif ps.hostname == "htn.to":
        service = "htnto"
    elif ps.hostname == "kvs.co": # Only redirects to kanvaso.com/show/CODE
        continue
    elif ps.hostname == "mypict.me": # TODO
        continue
    elif ps.hostname == "lnk.ms":
        service = "lnkms"
    elif ps.hostname == "ustre.am":
        service = "ustream"
    elif ps.hostname == "tiny.cc":
        service = "tinycc"
    elif ps.hostname == "klout.com": # Not a shorturl
        continue
    elif ps.hostname == "qbkn.info": # Spam domain
        continue
    elif ps.hostname == "flic.kr": # Does weird internal redirect
        continue
    elif ps.hostname in ["durl.dk", "durl.me"]:
        service = "durldk"
    elif ps.hostname == "sns.mx": # Only redirects to www.snsanalytics.com/CODE
        continue
    elif ps.hostname == "twurl.nl":
        service = "twurlnl"
    elif ps.hostname == "vsb.li": # Does weird internal redirect TODO
        continue
    elif ps.hostname == "www.infotop.jp": # Advertisement network
        continue
    elif ps.hostname == "po.st":
        service = "post"
    elif ps.hostname == "moby.to":
        service = "mobyto"
    elif ps.hostname == "bull.hn": # Recruiting network
        continue
    elif ps.hostname == "pulse.me":
        if ps.path[0:3] != "/s/":
            continue
        code = ps.path[3:]
        service = "pulseme"
    elif ps.hostname == "twitvid.com": # Only redirects to www.twitvid.com/CODE
        continue
    elif ps.hostname == "ff.im":
        service = "ffim"
    elif ps.hostname == "itun.es":
        service = "itunes"
    elif ps.hostname == "yfrog.us": # Only redirects fo yfrog.com/CODE
        continue
    elif ps.hostname == "post.ly":
        service = "postly"
    elif ps.hostname == "awe.sm":
        service = "awesm"
    elif ps.hostname == "r.ebay.com": # Does not seem to work
        continue
    elif ps.hostname == "bible.us": # Not a shorturl
        continue
    elif ps.hostname == "facebook.com": # Not a shorturl
        continue
    elif ps.hostname == "kom.ps":
        service = "komps"
    elif ps.hostname == "tou.ch": # Does weird internal redirect
        continue
    elif ps.hostname == "gu.com": # Only redirects to www.guardian.co.uk/CODE
        continue
    elif ps.hostname == "mixi.at": # Does weird internal redirect
        continue
    elif ps.hostname == "froo.co": # Does a second redirect TODO
        continue
    elif ps.hostname == "fc2.in": # Is not Bitly Pro, but redirects to j.mp/CODE
        service = "bitly"
        verify = True
    elif ps.hostname == "gomiso.com": # Only internal redirect(?)
        continue
    elif ps.hostname == "twitter.com": # Not a shorturl
        continue
    elif ps.hostname == "yahoo.jp": # URLs are not stable
        continue
    elif ps.hostname == "y.ahoo.it": # URLs are not stable
        continue

    if service and code:
        if verify:
            longurl = tinyback.services.factory(service).fetch(code)
            if not longurl:
                continue
        db = db_manager.get(service)
        db.set(code, longurl)

db_manager.close()
