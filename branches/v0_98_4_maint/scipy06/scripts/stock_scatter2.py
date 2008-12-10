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

        close = dailydata.adjclose

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
        self.size = 10*nx.log(self.totalvolume)
        self.color = self.totalreturn

    def plotraw(self):
        fig = figure()
        dd = self.dailydata
        fig.clf()
        ax1 = fig.add_subplot(211)
        ax1.plot_date(dd.date, dd.adjclose, '-')
        
        ax2 = fig.add_subplot(212) # sharex
        ax2.bar(dd.date, dd.volume)
        ax2.xaxis_date()

        ## snippet 3 customizations
        # grids, labels and titles
        ax1.grid(True)
        ax2.grid(True)
        ax1.set_ylabel('Closing price')
        ax2.set_ylabel('Daily volume')
        ax1.set_title('Closing prices of %s'%self.dailydata.ticker)

        # use nicer tick locating and formatting
        from matplotlib.dates import DateFormatter, MonthLocator
        from matplotlib.ticker import FuncFormatter, ScalarFormatter
        #tickloc = MonthLocator()
        tickloc = MonthLocator((1,4,7,10))
        tickfmt = DateFormatter('%b %Y')
        ax2.xaxis.set_major_formatter(tickfmt)
        ax2.xaxis.set_major_locator(tickloc)

        
        def fmt_millions(x, pos=None):
            return '%d'%int(x/1e6)

        class PriceFormatter(ScalarFormatter):
            def __call__(self, x, pos):
                if pos==0: return ''
                else: return ScalarFormatter.__call__(self, x, pos)
            
        ax1.yaxis.set_major_formatter(PriceFormatter())            
        ax2.yaxis.set_major_formatter(FuncFormatter(fmt_millions))

        # fix the toolbar formatting
        ax1.fmt_xdata = DateFormatter('%Y-%m-%d')
        ax2.fmt_xdata = DateFormatter('%Y-%m-%d')

        # make the upper ticks invisible, the lower ticks rotated, and
        # adjust the subplot params
        for label in ax1.xaxis.get_ticklabels():
            label.set_visible(False)

        for label in ax2.xaxis.get_ticklabels():
            label.set_rotation(40)

        fig.subplots_adjust(bottom=0.15, hspace=0.05)        

        fig.canvas.manager.show()

class ScatterPoints:
    def __init__(self, ax, pnts, **kwargs):
        """
        ax is an Axes instance        
        pnts is a sequence of ScatterPoint instances
        kwargs are passwd on to scatter
        """
        self.ax = ax
        self.pnts = pnts
        self.xs, self.ys, self.sizes, self.colors = map(nx.array, zip(*[(p.x, p.y, p.size, p.color) for p in pnts]))
        self.ax.scatter(self.xs, self.ys, self.sizes, self.colors, **kwargs)
        
        self.ax.figure.canvas.mpl_connect('button_press_event', self.onpress)

    def onpress(self, event):
        if event.inaxes != self.ax: return
        if event.button!=1: return
        # click location in screen coords
        x, y = nx.array((event.x, event.y))
        tx, ty = event.inaxes.transData.numerix_x_y(self.xs, self.ys)
        d = nx.sqrt((x-tx)**2 + (y-ty)**2)
        ind = nx.nonzero(d<5)
        for i in ind:
            self.pnts[i].plotraw()


if 1:
    fig = figure(1); fig.clf()
    ax = fig.add_subplot(111)

    points = ScatterPoints(ax, [DailyPoint(dailydata) for dailydata in tickerd.values()], alpha=0.75)

show()

