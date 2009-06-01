import sys
import SimpleXMLRPCServer
import logging
from datetime import datetime

from currency_server import db

LOGFILE = '/var/currency_server/access.log'

logging.basicConfig(filename=LOGFILE, level=logging.INFO, format='%(asctime)s %(message)s')

def handler(req):
    req.write(dispatcher._marshaled_dispatch(req.read()))
    return 0 # apache.OK

dispatcher = SimpleXMLRPCServer.SimpleXMLRPCDispatcher(True, 'utf-8')

# Test method

def hello():
    return sys.version
dispatcher.register_function(hello, 'hello')

# Wrapper around the get_rates() method

RATES_DB = db.RatesDB(db.DB_PATH)
def get_CAD_values(start, end, currency):
    logging.info('%s %s %s' % (start, end, currency))
    start = datetime.strptime(start.value, "%Y%m%dT%H:%M:%S")
    end = datetime.strptime(end.value, "%Y%m%dT%H:%M:%S")
    return RATES_DB.get_CAD_values(start, end, currency)
dispatcher.register_function(get_CAD_values, 'get_CAD_values')
