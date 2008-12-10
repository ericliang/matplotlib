import pylab
import mpl_toolkits.mplsizer as mplsizer

# Demonstration of minsize use.

# This is known to not currently work.

rows = 5
cols = 10

f = pylab.figure(figsize=(0.1,0.1))
sizer = mplsizer.MplGridSizer(cols=cols)
frame = mplsizer.MplSizerFrame( f )
frame.SetSizer(sizer)#,expand=1)

minsize = 1.0
for i in range(rows):
    for j in range(cols):
        ax=f.add_axes([0,0,1,1],label='%d,%d'%(i,j))#,frameon=False)
        ax.text(0.5,0.5,'%d,%d'%(i,j))
        ax.set_xticks([])
        ax.set_yticks([])
        sizer.Add( ax, minsize=(.5,.75),border=0.05,all=1)#, expand=1 )
frame.Layout()
pylab.show()
