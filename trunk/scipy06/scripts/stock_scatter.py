import os, sys, datetime, csv, time
import matplotlib.numerix as nx
from matplotlib.dates import date2num, datestr2num
from matplotlib.mlab import load
from pylab import figure, show, draw
import dateutil.parser

datadir = os.path.join('..', 'data')
tickerfile = os.path.join(datadir, 'nasdaq100.dat')
tickers = [line.strip() for line in file(tickerfile)]

months = dict(Jan=1, Feb=2, Mar=3, Apr=4, May=5, Jun=6, Jul=7, Aug=8, Sep=9,
              Oct=10, Nov=11, Dec=12)
def to_datenum2(s):
    d,m,y = s.split('-')
    return date2num(datetime.date(int(y), months[m], int(d)))

class DailyData:

    def __init__(self, ticker):
        # load assumes floats unless you provide a converter
        # dictionary keyed by column number
        self.ticker = ticker
        tickerfile = os.path.join(datadir, '%s.csv'%ticker)
        
        # datestr2num is slow but it's easy
        (self.date, self.open, self.high, self.low,
         self.close, self.volume, self.adjclose) = load(
            tickerfile, delimiter=',',
            converters={0:to_datenum2},            
            #converters={0:datestr2num},
            skiprows=1, unpack=True)            

if 1:  # pay the load only once in interactive mode
    tickerd = dict()
    for ticker in tickers:
        tickerd[ticker] = DailyData(ticker)


class ScatterPoint:
    """
    Create an interface to scatter plot point where individual points
    can be selected and introspected.  We can represent four
    dimensions in a scatter: x, y, size and color.  The object will
    provide a method for each of those, and a method called"plotdata"
    which will provide a detail plot of the underlying data

    Derived classes mush define the following attributes 
      x: x axis data value as a scale'
      y: y axis data value as a scalar'
      size: the size the scatter marker in points^2'
      color: the color of the marker; can be a colormappable scalar'
      """

    def plotraw(self, fig):
        'plot the raw time data in the Figure instance'
        pass



class DailyPoint(ScatterPoint):

    def __init__(self, dailydata):
        self.dailydata = dailydata

        close = dailydata.close
        # daily returns
        self.dailyreturn = (close[1:]-close[:-1])/close[:-1]
        # total returns
        self.totalreturn = (close[-1] - close[0])/close[0]
        # mean of daily returns
        self.mudaily = nx.mlab.mean(self.dailyreturn)
        # std of daily returns
        self.sigmadaily = nx.mlab.std(self.dailyreturn)
        # average daily volume of shares traded
        self.totalvolume = nx.mlab.mean(dailydata.volume)
        # the lag1 autocorrelation of daily returns
        self.lag1corr = nx.mlab.corrcoef(self.dailyreturn[1:], self.dailyreturn[:-1])[0,1]


        # Define the attributes needed for the scatter point interface
        self.x = self.lag1corr
        self.y = self.sigmadaily
        self.size = 10*nx.log(self.totalvolume)
        self.color = self.totalreturn

    def plotraw(self, fig):
        dd = self.dailydata
        fig.clf()
        ax1 = fig.add_subplot(211)
        ax1.plot_date(dd.date, dd.close, '-')
        
        ax2 = fig.add_subplot(212, sharex=ax1) # sharex
        ax2.bar(dd.date, dd.volume)
        ax2.xaxis_date()

        # hide tick labels on 211
        # share x-axes
        # improve tick formatting
        # toolbar tick formatting
        # xlabels, ylabels and titles
        # volume formatting

        # make the upper axes xticks invisible
        for label in ax1.xaxis.get_ticklabels():
            label.set_visible(False)

        # rotate the lower axes ticks
        for label in ax2.xaxis.get_ticklabels():
            label.set_rotation(45)

        # use nicer tick locating and formatting
        from matplotlib.dates import DateFormatter, MonthLocator
        from matplotlib.ticker import FuncFormatter
        tickloc = MonthLocator()
        tickfmt = DateFormatter('%b %Y')
        ax2.xaxis.set_major_formatter(tickfmt)
        ax2.xaxis.set_major_locator(tickloc)

        # fix the y axis volume formatter
        def millions(x, pos=None):
            return '%d'%int(x/1e6)
        ax2.yaxis.set_major_formatter(FuncFormatter(millions))

        # fix the toolbar formatting
        ax1.fmt_xdata = DateFormatter('%Y-%m-%d')
        ax2.fmt_xdata = DateFormatter('%Y-%m-%d')
        
if 1:
    points = [DailyPoint(dailydata) for dailydata in tickerd.values()]
    data = [(p.x, p.y, p.size, p.color) for p in points]
    x, y, size, color = zip(*data)

if 0:
    fig = figure()
    ax = fig.add_subplot(111)
    ax.scatter(x, y, size, color, alpha=0.75)

if 1:
    fig = figure(2)
    p = points[0]
    p.plotraw(fig)
    draw()
show()
