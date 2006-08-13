import os, sys, datetime, csv, time
import matplotlib.numerix as nx
from matplotlib.dates import date2num, datestr2num
from matplotlib.mlab import load
import dateutil.parser

datadir = os.path.join('..', 'data')
tickerfile = os.path.join(datadir, 'nasdaq100.dat')
tickers = [line.strip() for line in file(tickerfile)]

def todatenum(s):
    #y, m, d = time.strptime(s, '%d-%b-%y')[:3]
    y,m,d = s.split('-')
    y = int(y)
    d = int(d)
    m = dict(Jan=1, Feb=2, Mar=3, Apr=4, May=5, Jun=6, Jul=7, Aug=8, Sep=9, Oct=10, Nov=11, Dec=12)[m]
    dt = datetime.date(y, m, d)
    n = date2num(dt)
    #return 1.
    return n

class StockDaily:

    def __init__(self, ticker):
        # load assumes floats unless you provide a converter
        # dictionary keyed by column number
        self.ticker = ticker
        tickerfile = os.path.join(datadir, '%s.csv'%ticker)
        #s = file(tickerfile).read()
        if 1:
            # datestr2num is slow but it's easy
            (self.date, self.open, self.high, self.low,
             self.close, self.volume, self.adjclose) = load(
                tickerfile, delimiter=',',
                converters={0:todatenum},            
                #converters={0:datestr2num},
                skiprows=1, unpack=True)            



tickerd = dict()
for ticker in tickers:
    tickerd[ticker] = StockDaily(ticker)
