from matplotlib.toolkits.basemap import Basemap, interp
from pylab import *
import cPickle

# read in data on lat/lon grid.
hgt = array(load('data/500hgtdata.gz'),'d')
lons = array(load('data/500hgtlons.gz'),'d')
lats = array(load('data/500hgtlats.gz'),'d')
lons, lats = meshgrid(lons,lats)

# set up map projection (lambert azimuthal equal area).
m = Basemap(-135.,-20.,45.,-20.,
             resolution='c',area_thresh=10000.,projection='laea',
             lat_0=90.,lon_0=-90.)

cmap = cm.jet
fig = figure(figsize=(6,6))

ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])

x,y = m(lons, lats)
cs = contour(x,y,hgt,15,linewidths=0.5,colors='k')
cs = contourf(x,y,hgt,15,cmap=cmap,colors=None)

# draw map.
m.drawcoastlines()

# draw parallels
delat = 30.
delon = 90.
circles = arange(10.,90.+delat,delat).tolist()
m.drawparallels(circles,labels=[0,0,1,1], fontsize=16)

# draw meridians
meridians = arange(0.,360.,delon)
m.drawmeridians(meridians,labels=[1,1,1,1],fontsize=16)


savefig('contour_small.png', dpi=50)
savefig('contour_large', dpi=120)
show()
