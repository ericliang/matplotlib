## snippet 1: date conversion function (OS X 10.3 bug)
def to_datenum1(s):
    'convert date strings like 6-Aug-06 to matplotlib datenums'
    y, m, d = time.strptime(s, '%d-%b-%y')[:3]
    return date2num(datetime.date(y,m,d))

## snippet 2: date conversion function 
months = dict(Jan=1, Feb=2, Mar=3, Apr=4, May=5, Jun=6, Jul=7, Aug=8, Sep=9,
              Oct=10, Nov=11, Dec=12)
def to_datenum2(s):
    d,m,y = s.split('-')
    return date2num(datetime.date(int(y), months[m], int(d)))

## snippet 3
        # make the upper axes xticks invisible
        for label in ax1.xaxis.get_xticklabels():
            label.set_visible(False)

        # rotate the lower axes ticks
        for label in ax2.xaxis.get_xticklabels():
            label.rotation(45)

        # use nicer tick locating and formatting
        from matplotlib.dates import DateFormatter, MonthLocator, FuncFormatter
        tickloc = MonthLocator()
        tickfmt = DateFormatter('%b %Y')
        ax2.xaxis.set_major_formatter(tickfmt)
        ax2.xaxis.set_major_locator(tickloc)

        # fix the y axis volume formatter
        def millions(x):
            return '%1.1f'%(x/1e6)
        ax2.yaxis.set_major_formatter(FuncFormatter(millions))

        # fix the toolbar formatting
        ax1.fmt_xdata = DateFormatter('%Y-%m-%d')
        ax2.fmt_xdata = DateFormatter('%Y-%m-%d')
        
