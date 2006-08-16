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
    y = int(y)
    if y>10: y+=1900
    else: y+= 2000
    return date2num(datetime.date(y, months[m], int(d)))

## snippet 3 - customizing a plot

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


## snippet 4: button press handling
def onpress(event):
    if not event.inaxes: return 
    if event.button!=1: return
    # click location in screen coords
    clickxy = nx.array((event.x, event.y))
    transform = event.inaxes.transData.xy_tup
    for p in points:
        # transform point center to screen coords
        pntxy = nx.array(transform((p.x, p.y)))
        d = dist(clickxy, pntxy)
        if d<5: # pixel space
            print 'hit!'
            p.plotraw()
