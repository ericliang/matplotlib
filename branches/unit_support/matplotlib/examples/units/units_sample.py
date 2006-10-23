
import matplotlib
matplotlib.use('Agg')

import matplotlib.basic_units as bu
import numpy as N
from matplotlib.pylab import *

cm = bu.BasicUnit('cm', 'centimeters')
inch = bu.BasicUnit('inch', 'inches')

inch.add_conversion_factor(cm, 2.54)
cm.add_conversion_factor(inch, 1/2.54)

lengths_cm = cm*N.arange(0, 10, 0.5)
# iterator test
print 'Testing iterators...'
for length in lengths_cm:
  print length

print 'Iterable() = ' + `iterable(lengths_cm)`

print lengths_cm
print lengths_cm.convert_to(inch)
print lengths_cm.convert_to(inch).get_value()

clf()
subplot(2,2,1)
plot(lengths_cm, 2.0*lengths_cm, xunits=cm, yunits=cm)
xlabel('in centimeters')
ylabel('in centimeters')
subplot(2,2,2)
plot(lengths_cm, 2.0*lengths_cm, xunits=cm, yunits=inch)
xlabel('in centimeters')
ylabel('in inches')
subplot(2,2,3)
plot(lengths_cm, 2.0*lengths_cm, xunits=inch, yunits=cm)
xlabel('in inches')
ylabel('in centimeters')
subplot(2,2,4)
plot(lengths_cm, 2.0*lengths_cm, xunits=inch, yunits=inch)
xlabel('in inches')
ylabel('in inches')
savefig('simple_conversion.png')

# radians formatting
def rad_fn(x,y):
  n = int((x / N.pi) * 2.0 + 0.25)
  if n == 0:
    return '0'
  elif n == 1:
    return r'$\pi/2$'
  elif n == 2:
    return r'$\pi$'
  elif n % 2 == 0:
    return r'$%s\pi$' % (n/2,)
  else:
    return r'$%s\pi/2$' % (n,)

clf()
radians = bu.BasicUnit('rad', 
                       'radians', 
                        tick_locators=(MultipleLocator(base=N.pi/2),
                                       NullLocator()),
                        tick_formatters=(FuncFormatter(rad_fn),
                                         NullFormatter()))
degrees = bu.BasicUnit('deg', 
                       'degrees',
                       tick_formatters=(FormatStrFormatter(r'$%i^\circ$'),
                                        NullFormatter()))
radians.add_conversion_factor(degrees, 180.0/N.pi)
degrees.add_conversion_factor(radians, N.pi/180.0)
x = N.arange(0, 15, 0.01) * radians
subplot(2,1,1)
plot(x, N.cos(x), xunits=radians)
xlabel('radians')
subplot(2,1,2)
plot(x, N.cos(x), xunits=degrees)
xlabel('degrees')

savefig('simple_cosine.png')
