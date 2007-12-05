import pylab
import numpy

# Demonstration of MplGridSizer use.

def labelax(ax,label):
    ax.text(0.5,0.5,label,
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax.transAxes,
           )

fig = pylab.figure(figsize=(8,6))

# Axes placement doesn't matter, but to make sure matplotlib doesn't
# simply return a previous Axes instance with the same bounding box,
# assign a different label to each Axes instance.

import matplotlib.toolkits.mplsizer as mplsizer

frame = mplsizer.MplSizerFrame( fig )
sizer = mplsizer.MplBoxSizer()#orientation='horizontal')
frame.SetSizer(sizer)#,expand=1)

x = numpy.linspace(0,2*numpy.pi,100)
y = numpy.sin(1*x+numpy.pi/2) + .5*numpy.sin(3*x)
cols = 3
rows = 4
hsizer = mplsizer.MplGridSizer(cols=cols)#,vgap_inch=0.1)
for r in range(rows):
    for c in range(cols):
        if r==1 and c==1:
            # This is how to add an empty element.
            ax = mplsizer.MplSizerElement()
        else:

            # The unique labels are required to generate separate Axes instances.
            ax = fig.add_axes([0,0,1,1],label='row %d col %d'%(r,c))

            ax.plot(x,y)
            labelax(ax,'%d,%d'%(r,c))
            if not (r==2 and c==2):
                # Draw tick labels on one Axes instance.
                pylab.setp(ax,'xticks',[])
                pylab.setp(ax,'yticks',[])

        # The "border" value below was hand-tuned to not overlap.
        hsizer.Add(ax,name='row %d, col %d'%(r,c),all=1,border=0.3,expand=1)

sizer.Add(hsizer,all=1,bottom=1,border=0.25,expand=1,option=1)

frame.Layout() # Trigger the layout within mplsizer.

pylab.show()
