import matplotlib
matplotlib.use('Agg')

import matplotlib.basic_units as bu
import numpy as N
from matplotlib.pylab import *

# create masked array
x = N.ma.MaskedArray((1,2,3,4,5,6,7,8), N.float64, mask=(1,0,1,0,0,0,1,0))

secs = bu.BasicUnit('s', 'seconds')
hertz = bu.BasicUnit('Hz', 'Hertz')
min = bu.BasicUnit('min', 'minutes')

secs.add_conversion_fn(hertz, lambda x:1./x)
secs.add_conversion_factor(min, 1/60.0)

clf()
subplot(3,1,1)
scatter(x, x)
xlabel('seconds')
ylabel('seconds')
axis([0,10,0,10])

subplot(3,1,2)
x_in_secs = secs*x
print x_in_secs
scatter(x_in_secs, x_in_secs, yunits=hertz)
xlabel('seconds')
ylabel('Hertz')
axis([0,10,0,1])

subplot(3,1,3)
x_in_secs = secs*x
scatter(x_in_secs, x_in_secs, yunits=hertz)
gca().set_yunits(min)
axis([0,10,0,1])
xlabel('seconds')
ylabel('minutes')
savefig('units-test-scatter.png')


