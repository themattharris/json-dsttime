# -*- encoding: utf-8 -*-
"""
Webservice which returns the correct UTC offset for a timezone on a given date
Author:  Matt Harris (matt [at] themattharris dot com)
Version: 0.1
Updated: 21 Sep 2009
License: MIT License (included file MIT-LICENSE)
"""
import time
import pytz
import simplejson as json

from pytz import timezone
from dateutil.parser import parse
from datetime import datetime
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/javascript'
        dt = self.request.get('dt', default_value=datetime.now().isoformat())
        tz = self.request.get('tz', default_value='UTC')
        data = json_dsttime(dt, tz)
        self.response.out.write(json.dumps(data))

def json_dsttime(isotime, tz='UTC'):
    error = None
    try:
        tz = timezone(tz)
    except pytz.UnknownTimeZoneError:
        return { '_dt': isotime, 'error': u'Unknown timezone provided.' }

    zulu = timezone('UTC')
    parsed = parse(isotime)
    utc = parsed.utctimetuple()
    format = "%Y-%m-%dT%H:%M:%S"
    utc = datetime.strptime(time.strftime(format, utc), format)
    local = tz.localize(utc)
    utc = zulu.localize(utc)
    is_dst = local.dst().seconds > 0

    json = { 'hour': local.hour, 'second': local.second,
        'minute': local.minute, 'day': local.day, 'month': local.month,
        'year': local.year, '_dt': isotime, 'local': local.isoformat(),
        'utc': utc.isoformat(), '_tz': tz.zone, 'dst': is_dst
    }
    return json

def main():
    application = webapp.WSGIApplication(
        [('/', MainPage)],
        debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()