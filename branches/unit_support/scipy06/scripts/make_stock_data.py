"""
Download the daily stock data for the NASDAQ 100 and put the results
in CSV files
"""
import datetime, urllib, os
 
datadir = os.path.join('..', 'data')
tickerfile = os.path.join(datadir, 'nasdaq100.dat')
startdate = datetime.date(2005,1,1)
enddate = datetime.datetime.now().date()

tickers = [line.strip() for line in file(tickerfile)]

urlfmt = 'http://table.finance.yahoo.com/table.csv?a=%(startmonth)d&b=%(startday)d&c=%(startyear)d&d=%(endmonth)d&e=%(endday)d&f=%(endyear)d&s=%(ticker)s&y=0&g=d&ignore=.csv'

for ticker in tickers:
    outfile = os.path.join(datadir, '%s.csv'%ticker)
    print 'fetching ticker %s to %s' % (ticker, outfile)
    if os.path.exists(outfile): continue # already have it

    props = dict(
        ticker = ticker.upper(),
        startmonth = startdate.month-1,
        startday = startdate.day,
        startyear = startdate.year,
        endmonth = enddate.month-1,
        endday = enddate.day,
        endyear = enddate.year)    
    
    url =  urlfmt % props
    urllib.urlretrieve(url, outfile)
