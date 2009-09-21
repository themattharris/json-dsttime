import time

try:
    import pytz
except ImportError:
    print 'The pytz library is required. Please download from http://pytz.sourceforge.net/'

from pytz import timezone
from dateutil.parser import parse
from datetime import datetime

def timeinfo(isotime, tz='UTC'):
    error = None
    try:
        tz = timezone(tz)
        zulu = timezone('UTC')
    except UnknownTimeZoneError:
        return jsonerror(isotime, u'Unknown timezone provided.')

    parsed = parse(isotime)
    utc = parsed.utctimetuple()
    format = "%Y-%m-%dT%H:%M:%S"
    utc = datetime.strptime(time.strftime(format, utc), format)
    local = tz.localize(utc)
    utc = zulu.localize(utc)
    is_dst = local.dst().seconds > 0
    
    json = { 'hour': local.hour, 'second': local.second,
        'minute': local.minute, 'day': local.day, 'month': local.month,
        'year': local.year, '_datetime': isotime, 'local': local.isoformat(),
        'utc': utc.isoformat(), '_timezone': tz.zone, 'dst': is_dst
    }
    return json

def jsonerror(isotime, msg):
    return { '_datetime': isotime, 'error': msg }
