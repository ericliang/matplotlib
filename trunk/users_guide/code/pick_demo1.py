from pylab import figure, show, nx
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from matplotlib.text import Text

fig = figure()
ax1 = fig.add_subplot(211)
ax1.set_title('click on points, rectangles or text', picker=True)
ax1.set_ylabel('ylabel', picker=True, bbox=dict(facecolor='red'))
line, = ax1.plot(nx.mlab.rand(100), 'o', picker=5)  # 5 points tolerance


ax2 = fig.add_subplot(212)

# pick the bars
bars = ax2.bar(range(10), nx.mlab.rand(10), picker=True)
for label in ax2.get_xticklabels():  
    label.set_picker(True)   # make the xtick labels pickable    

# this function will be called when one of the picker Artists is
# clicked on
def onpick1(event):
    if isinstance(event.artist, Line2D):
        thisline = event.artist
        xdata = thisline.get_xdata()
        ydata = thisline.get_ydata()
        ind = event.ind
        print 'onpick1 line:', zip(nx.take(xdata, ind), nx.take(ydata, ind))
    elif isinstance(event.artist, Rectangle):
        patch = event.artist
        print 'onpick1 patch:', patch.get_verts()
    elif isinstance(event.artist, Text):
        text = event.artist
        print 'onpick1 text:', text.get_text()

# now register your function to get a callback on a pick event
fig.canvas.mpl_connect('pick_event', onpick1)
show()
