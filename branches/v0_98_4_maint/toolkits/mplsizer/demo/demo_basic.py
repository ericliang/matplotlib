import pylab
import matplotlib.numerix as nx

# Demonstration of basic mplsizer use.

# This example shows use with standard, simple pylab-style plots.

def labelax(ax,label):
    ax.text(0.5,0.5,label,
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax.transAxes,
           )
    
fig = pylab.figure()

# Axes placement doesn't matter, but to make sure matplotlib doesn't
# simply return a previous Axes instance with the same bounding box,
# assign a different label to each Axes instance.

# Axes are drawn in the order created. Thus this Axes instance will be
# drawn first and will thus be "lowest".

# In this case, "lowest" is present for debugging purposes. At the end
# of this script, a call to lowest.set_position() set's the position
# to a private mplsizer attribute. It's naughty to use the private
# attribute, but, hey, this is for debugging only, so it's OK, right?

lowest=fig.add_axes([0,0,1,1],label='lowest')
lowest.axesPatch.set_facecolor('green')
pylab.setp(lowest,'xticks',[])
pylab.setp(lowest,'yticks',[])


# Now add some axes with real plots...

a=fig.add_axes([0,0,1,1],label='a')
labelax(a,'a')
a.plot([1,2,3],[4,5,6],'r-')


b=fig.add_axes([0,0,1,1],label='b')
labelax(b,'b')
theta = nx.arange(0,2*nx.pi,0.01)
x = nx.cos(theta)
y = nx.sin(theta)
b.plot(x,y,'b-')


b2=fig.add_axes([0,0,1,1],label='b2')
labelax(b2,'b2')

more_plots = 1
if more_plots:
    c=fig.add_axes([0,0,1,1],label='c')
    labelax(c,'c')

    d=fig.add_axes([0,0,1,1],label='d')
    labelax(d,'d')



if 1:
    # Now perform the mplsizer stuff
    
    import mpl_toolkits.mplsizer as mplsizer
    
    frame = mplsizer.MplSizerFrame( fig )
    sizer = mplsizer.MplBoxSizer()
    frame.SetSizer(sizer)

    sizer.Add(a,name='a',expand=1)
    sizer.Add(b,name='b',all=0,left=1,border=0.2)
    sizer.Add(b2,name='b2')

    if more_plots:
        hsizer = mplsizer.MplBoxSizer(orientation='horizontal')
        hsizer.Add(c,name='c',option=1,align_bottom=1)
        hsizer.Add(d,name='d',align_centre=1)
        sizer.Add(hsizer,all=0,bottom=1,border=0.5,expand=1,option=1)

    frame.Layout() # triggers layout

    # It's naughty to use the private attribute, but, hey, this is for
    # debugging only, so it's OK, right?
    lowest.set_position(hsizer._rect)

pylab.show()
