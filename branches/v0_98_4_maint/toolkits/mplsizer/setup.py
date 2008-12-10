from setuptools import setup

setup(name='mplsizer',
      author='Andrew Straw',
      author_email='strawman@astraw.com',
      description='layout engine for matplotlib based on wxPython model',
      long_description="""\
mplsizer is a layout engine that re-creates the wxPython idioms for
use within matplotlib. For example, you may create an MplBoxSizer and
add MplSizerElements to it, including with optional parameters such as
"expand" and "border".

mplsizer currently requires the use of setuptools for "namespace
package" support.
""",
      version='0.1',
      license='MIT',
      url='http://matplotlib.sourceforge.net/',
      packages=['mpl_toolkits','mpl_toolkits.mplsizer'],
      namespace_packages = ['mpl_toolkits'],
      )
