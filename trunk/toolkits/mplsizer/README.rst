mplsizer
********

mplsizer is a layout engine for matplotlib_ based on wxPython model. It
is released under the MIT license.

.. _matplotlib: http://matplotlib.sourceforge.net/

svn access
==========

The official svn repository is at
https://matplotlib.svn.sourceforge.net/svnroot/matplotlib/trunk/toolkits/mplsizer/

unofficial git mirror
=====================

An un-official git mirror is made of the source code repository at
http://github.com/astraw/mplsizer. You can make a copy of this
repository with::

  git clone --origin svn git@github.com:astraw/mplsizer.git
  cd mplsizer/
  git svn init --trunk=trunk/toolkits/mplsizer --prefix=svn/ https://matplotlib.svn.sourceforge.net/svnroot/matplotlib
  git svn rebase -l
