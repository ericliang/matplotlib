from matplotlib.matlab import *

dt = 0.01
t = arange(dt, 20.0, dt)

subplot(311)
semilogx(t, exp(-t/5.0))

subplot(312)
semilogx(t, sin(2*pi*t))

subplot(313)
loglog(t, exp(-t/10.0))
#savefig('log_demo')
show()
