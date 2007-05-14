from pylab import figure, nx, show
# you can specify the xypoint and the xytext in different
# positions and coordinate systems, and optionally turn on a
# connecting line and mark the point with a marker.  Annotations
# work on polar axes too.  In the example below, the xy point is
# in native coordinates (xycoords defaults to 'data').  For a
# polar axes, this is in (theta, radius) space.  The text in this
# example is placed in the fractional figure coordinate system.
# Text keyword args like horizontal and vertical alignment are
# respected
fig = figure()
ax = fig.add_subplot(111, polar=True)
r = nx.arange(0,1,0.001)
theta = 2*2*nx.pi*r
line, = ax.plot(theta, r, color='#ee8d18', lw=3)

ind = 800
thisr, thistheta = r[ind], theta[ind]
ax.plot([thistheta], [thisr], 'o')
ax.annotate('a polar annotation',
            xy=(thistheta, thisr),  # theta, radius
            xytext=(0.05, 0.05),    # fraction, fraction
            textcoords='figure fraction',
            arrowprops=dict(facecolor='black', shrink=0.05),
            horizontalalignment='left',
            verticalalignment='bottom',
            )
fig.savefig('../figures/annotation_demo.png')
fig.savefig('../figures/annotation_demo.ps')

show()
