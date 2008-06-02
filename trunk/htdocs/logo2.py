"""
Thanks to Tony Yu <tsyu80@gmail.com> for the logo design
"""

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.mlab as mlab
from pylab import rand

mpl.rcParams['xtick.labelsize'] = 6
mpl.rcParams['ytick.labelsize'] = 6
mpl.rcParams['axes.edgecolor'] = 'gray'


axalpha = 0.05
#figcolor = '#EFEFEF'
figcolor = 'white'
dpi = 80
fig = plt.figure(figsize=(7, 1.5),dpi=dpi)
fig.figurePatch.set_edgecolor(figcolor)
fig.figurePatch.set_facecolor(figcolor)


def add_math_background():
    ax = fig.add_axes([0., 0., 1., 1.])

    text = []
    text.append((r"$W^{3\beta}_{\delta_1 \rho_1 \sigma_2} = U^{3\beta}_{\delta_1 \rho_1} + \frac{1}{8 \pi 2} \int^{\alpha_2}_{\alpha_2} d \alpha^\prime_2 \left[\frac{ U^{2\beta}_{\delta_1 \rho_1} - \alpha^\prime_2U^{1\beta}_{\rho_1 \sigma_2} }{U^{0\beta}_{\rho_1 \sigma_2}}\right]$", (0.7, 0.2), 20))
    text.append((r"$\frac{d\rho}{d t} + \rho \vec{v}\cdot\nabla\vec{v} = -\nabla p + \mu\nabla^2 \vec{v} + \rho \vec{g}$",
                (0.35, 0.9), 20))
    text.append((r"$\int_{-\infty}^\infty e^{-x^2}dx=\sqrt{\pi}$",
                (0.15, 0.3), 25))
    #text.append((r"$E = mc^2 = \sqrt{{m_0}^2c^4 + p^2c^2}$",
    #            (0.7, 0.42), 30))
    text.append((r"$F_G = G\frac{m_1m_2}{r^2}$",
                (0.85, 0.7), 30))
    for eq, (x, y), size in text:
        ax.text(x, y, eq, ha='center', va='center', color="blue", alpha=0.25,
                transform=ax.transAxes, fontsize=size)
    ax.set_axis_off()
    return ax

def add_matplotlib_text(ax):
    ax.text(0.3, 0.5, 'matplotlib', color='black', fontsize=70,
               ha='left', va='center', alpha=1.0, transform=ax.transAxes)

def add_polar_bar():
    ax = fig.add_axes([0.05, 0.05, 0.2, 0.9], polar=True)
    ax.axesPatch.set_alpha(axalpha)
    N = 15
    arc = 2. * np.pi
    theta = np.arange(0.0, arc, arc/N)
    radii = 10 * np.random.rand(N)
    width = np.pi / 4 * np.random.rand(N)
    bars = ax.bar(theta, radii, width=width, bottom=0.0)
    for r, bar in zip(radii, bars):
        bar.set_facecolor(cm.jet(r/10.))
        bar.set_alpha(0.6)

def add_histogram():
    ax = fig.add_axes([0.325, 0.125, 0.2, 0.4])
    ax.axesPatch.set_alpha(axalpha)
    mu, sigma = 100, 15
    x = mu + sigma * np.random.randn(500)
    # the histogram of the data
    n, bins, patches = ax.hist(x, 15, normed=1, facecolor='green',
                               edgecolor='green', alpha=0.5)
    y = mlab.normpdf(bins, mu, sigma)
    l = ax.plot(bins, y, 'r', lw=1)
    ax.set_xlim(-4*sigma + mu, 4*sigma + mu)

def add_scatter():
    ax = fig.add_axes([0.6, 0.125, 0.15, 0.4])
    ax.axesPatch.set_alpha(axalpha)
    N = 40
    volume = 100 * rand(N)
    color = 256 * rand(N)
    darkgray = [0.2] * 3
    plt.scatter(rand(N), rand(N), c=color, s=volume, alpha=0.75,
                edgecolor=darkgray)
    plt.axis('tight')
    ax.set_yticks([])
    ax.set_xticks([])
    #ax.set_axis_off()

def add_pcolor():
    ax = fig.add_axes([0.75, 0.125, 0.2, 0.4])
    ax.axesPatch.set_alpha(axalpha)
    x = np.linspace(-3.0, 3.0, 200)
    X,Y = np.meshgrid(x, x)
    Z = (1- X/2 + X**5 + Y**3) * np.exp(-X**2-Y**2)
    limits = (-3,3,-3,3)
    cmap = cm.RdGy_r#(np.linspace(0.2, 1))
    im = plt.imshow(Z, interpolation='bilinear', origin='lower',
                    cmap=cmap, extent=limits)
    levels = np.arange(-1.2,1.6,0.4)
    cset = plt.contour(Z, levels, cmap=cm.hot, origin='lower', extent=limits)
    plt.clabel(cset, inline=1, fmt='%1.1f', fontsize=4)
    plt.colorbar()
    #ax.set_axis_off()

def add_pcolor2():
    ax = fig.add_axes([0.3, 0.125, 0.25, 0.4], aspect='auto')
    ax.axesPatch.set_alpha(axalpha)
    x = np.linspace(-3.0, 3.0, 200)
    X,Y = np.meshgrid(x, x)
    Z = (1- X/2 + X**5 + Y**3) * np.exp(-X**2-Y**2)
    limits = (-3,3,-3,3)
    cmap = cm.RdGy_r#(np.linspace(0.2, 1))
    im = plt.imshow(Z, interpolation='bilinear', origin='lower',
                    cmap=cmap, extent=limits, aspect='auto')
    levels = np.arange(-1.2,1.6,0.4)
    cset = plt.contour(Z, levels, cmap=cm.hot, origin='lower', extent=limits)
    plt.clabel(cset, inline=1, fmt='%1.1f', fontsize=4)
    #plt.colorbar()
    #ax.set_axis_off()

if __name__ == '__main__':
    main_axes = add_math_background()
    add_polar_bar()
#    add_histogram()
#    add_scatter()
# add_pcolor()
    #add_pcolor2()
    add_matplotlib_text(main_axes)
    fig.savefig('logo2.png', facecolor=figcolor, edgecolor=figcolor, dpi=dpi)
    plt.show()


