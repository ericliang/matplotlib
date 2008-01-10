from mpl_toolkits.basemap import Basemap, interp
from pylab import *

# read in data on lat/lon grid.
hgt = load('data/500hgtdata.gz')
lons = load('data/500hgtlons.gz')
lats = load('data/500hgtlats.gz')
lons, lats = meshgrid(lons,lats)

# set up map projection (lambert azimuthal equal area).
m = Basemap(projection='nplaea',lon_0=-90,boundinglat=15.,resolution='c')

cmap = cm.jet
fig = figure(figsize=(6,6))

ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])

x,y = m(lons, lats)
cs = m.contour(x,y,hgt,15,linewidths=0.5,colors='k')
cs = m.contourf(x,y,hgt,15,cmap=cm.jet)

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
