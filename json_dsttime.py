# -*- encoding: utf-8 -*-
"""
Webservice which returns the correct UTC offset for a timezone on a given date
Author:  Matt Harris (matt [at] themattharris dot com)
Version: 0.1
Updated: 21 Sep 2009

Copyright (c) 2009 Matt Harris (http://themattharris.com)

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
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
    formatz = "%Y-%m-%dT%H:%M:%S%Z"
    try:
        utc = datetime.strptime(time.strftime(formatz, utc), formatz)
    except ValueError:
        utc = datetime.strptime(time.strftime(format, utc), format)

    utc = zulu.localize(utc)
    local = utc.astimezone(tz)
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