import os, sys, datetime, csv, time
import matplotlib.numerix as nx
from matplotlib.dates import date2num, datestr2num
from matplotlib.mlab import load, dist
from pylab import figure, show, draw
import dateutil.parser

datadir = os.path.join('..', 'data')
tickerfile = os.path.join(datadir, 'nasdaq100.dat')
tickers = [line.strip() for line in file(tickerfile)]

def autocorr(x, lag=1):
    """Returns the autocorrelation x."""
    x = nx.asarray(x)
    mu = nx.mlab.mean(x)
    sigma = nx.mlab.std(x)
    return nx.dot(x[:-lag]-mu, x[lag:]-mu)/(sigma**2.)/(len(x) - lag)

# snippet 2 date converters

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
            #converters={0:to_datenum2},            
            converters={0:datestr2num},
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

    def plotraw(self):
        'plot the raw data'
        pass



class DailyPoint(ScatterPoint):

    def __init__(self, dailydata):
        self.dailydata = dailydata

        close = dailydata.close

        mu, sigma = nx.mlab.mean, nx.mlab.std

        # compute some statistics of daily and total returns
        self.dailyreturn = g = (close[1:]-close[:-1])/close[:-1]
        self.totalreturn = (close[-1] - close[0])/close[0]
        self.mudaily = mu(g)
        self.sigmadaily = sigma(g)
        self.totalvolume = sigma(dailydata.volume)
        self.lag1corr = autocorr(g, lag=1)

        # Assign the attributes needed for the scatter point interface
        self.x = self.lag1corr
        self.y = self.sigmadaily
        self.size = nx.log(self.totalvolume)
        self.color = self.totalreturn

    def plotraw(self):
        fig = figure()
        dd = self.dailydata
        fig.clf()
        ax1 = fig.add_subplot(211)
        ax1.plot_date(dd.date, dd.close, '-')
        
        ax2 = fig.add_subplot(212) # sharex
        ax2.bar(dd.date, dd.volume)
        ax2.xaxis_date()

        ## snippet 3 customizations

        draw()

## snippet 4: button press handling
        
if 1:
    points = [DailyPoint(dailydata) for dailydata in tickerd.values()]
    data = [(p.x, p.y, p.size, p.color) for p in points]
    x, y, size, color = zip(*data)

    fig = figure(1); fig.clf()
    ax = fig.add_subplot(111)
    ax.scatter(x, y, size, color, alpha=0.75)
    #fig.canvas.mpl_connect('button_press_event', onpress)

show()
