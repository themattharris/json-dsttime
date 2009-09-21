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
        dt = self.request.get('dt', 
            default_value=datetime.utcnow().isoformat())
        awaytz = self.request.get('to_tz', default_value='UTC')
        hometz = self.request.get('from_tz', default_value='UTC')
        data = json_dsttime(dt, awaytz, hometz)
        self.response.out.write(json.dumps(data))

def json_dsttime(isotime, awaytz='UTC', hometz='UTC'):
    error = None
    try:
        awaytz = timezone(awaytz)
    except pytz.UnknownTimeZoneError:
        return { '_dt': isotime, 'error': u'Unknown timezone provided.' }

    try:
        hometz = timezone(hometz)
    except pytz.UnknownTimeZoneError:
        return { '_dt': isotime, 'error': u'Unknown home timezone provided.' }

    zulu = timezone('UTC')
    parsed = parse(isotime)
    hometime = parsed.timetuple()
    format = "%Y-%m-%dT%H:%M:%S"
    formatz = "%Y-%m-%dT%H:%M:%S%Z"
    try:
        hometime = datetime.strptime(
            time.strftime(formatz, hometime), formatz)
    except ValueError:
        hometime = datetime.strptime(
            time.strftime(format, hometime), format)

    homedt = hometz.localize(hometime)
    awaydt = homedt.astimezone(awaytz)
    utc = homedt.astimezone(zulu)
    is_dst = awaydt.dst().seconds > 0

    json = { 'hour': awaydt.hour, 'second': awaydt.second,
        'minute': awaydt.minute, 'day': awaydt.day, 'month': awaydt.month,
        'year': awaydt.year, '_dt': isotime, 'homedt': homedt.isoformat(),
        'awaydt': awaydt.isoformat(), 'utc': utc.isoformat(), 
        '_totz': awaytz.zone, '_fromtz': hometz.zone,
        'dst': is_dst
    }
    return json

def main():
    application = webapp.WSGIApplication(
        [('/', MainPage)],
        debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()