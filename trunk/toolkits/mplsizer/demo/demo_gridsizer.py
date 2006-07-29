import pylab
import matplotlib.numerix as nx

# Demonstration of MplGridSizer use.

def labelax(ax,label):
    ax.text(0.5,0.5,label,
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax.transAxes,
           )
    
fig = pylab.figure(figsize=(1,1))

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


a=fig.add_axes([0,0,1,1],label='a')
labelax(a,'a')
a.plot([1,2,3],[4,5,6],'r-')

b=fig.add_axes([0,0,1,1],label='b') # make sure we don't get same axes
labelax(b,'b')
theta = nx.arange(0,2*nx.pi,0.01)
x = nx.cos(theta)
y = nx.sin(theta)
b.plot(x,y,'b-')

b2=fig.add_axes([0,0,1,1],label='b2') # make sure we don't get same axes
labelax(b2,'b2')

if 1:
    # Now perform the mplsizer stuff

    import matplotlib.toolkits.mplsizer as mplsizer
    
    frame = mplsizer.MplSizerFrame( fig )
    sizer = mplsizer.MplBoxSizer()#orientation='horizontal')
    frame.SetSizer(sizer)#,expand=1)

    sizer.Add(a,name='a',expand=1)#,option=1)#,expand=1)
    sizer.Add(b,name='b',all=0,left=1,border=0.2)
    sizer.Add(b2,name='b2')


    if 1:
        cols = 3
        rows = 4
        hsizer = mplsizer.MplGridSizer(cols=cols)#,vgap_inch=0.1)
        for r in range(rows):
            for c in range(cols):
                if r==1 and c==1:
                    ax = mplsizer.MplSizerElement() # make sure we can add an empty element
                else:
                    ax = fig.add_axes([0,0,1,1],label='row %d col %d'%(r,c))
                    labelax(ax,'%d,%d'%(r,c))
                    pylab.setp(ax,'xticks',[])
                    pylab.setp(ax,'yticks',[])
                hsizer.Add(ax,name='row %d, col %d'%(r,c),expand=1)#,border=0.1)
        sizer.Add(hsizer,all=1,bottom=1,border=0.25,expand=1,option=1)#,align_right=1)

    frame.Layout() # triggers layout
    
    # It's naughty to use the private attribute, but, hey, this is for
    # debugging only, so it's OK, right?
    lowest.set_position(hsizer._rect)

pylab.show()
