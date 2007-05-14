from pylab import figure, show, nx

def line_picker(line, mouseevent):
    """
    find the points within a certain distance from the mouseclick in
    data coords and attach some extra attributes, pickx and picky
    which are the data points that were picked
    """
    if mouseevent.xdata is None: return False, dict()
    xdata = line.get_xdata()
    ydata = line.get_ydata()
    maxd = 0.05
    d = nx.sqrt((xdata-mouseevent.xdata)**2. + (ydata-mouseevent.ydata)**2.)

    ind = nx.nonzero(nx.less_equal(d, maxd))
    if len(ind):
        pickx = nx.take(xdata, ind)
        picky = nx.take(ydata, ind)
        props = dict(ind=ind, pickx=pickx, picky=picky)
        return True, props
    else:
        return False, dict()

def onpick2(event):
    print 'onpick2 line:', event.pickx, event.picky

fig = figure()
ax1 = fig.add_subplot(111)
ax1.set_title('custom picker for line data')
line, = ax1.plot(nx.mlab.rand(100), nx.mlab.rand(100), 'o', picker=line_picker)
fig.canvas.mpl_connect('pick_event', onpick2)

show()
