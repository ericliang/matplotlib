import os, sys, glob, shutil
import matplotlib

MPL_SRC = os.environ.get('MPL_SRC', '/home/jdhunter/mpl')
MPL_SRC = '/home/jdhunter/mpl'


os.system('rm -rf examples')
os.system('tar -cv -C ~/mpl examples --exclude .svn --exclude Agg --exclude PDF --exclude PS --exclude Template|tar x')
os.system('zip -r -o matplotlib_examples_%s.zip examples'%matplotlib.__version__)

os.system('rm -rf doc')
os.system('tar -cv -C ~/mpl doc/devel doc/users --exclude .svn --exclude png |tar x')

os.system('cp ../users_guide/users_guide.pdf users_guide_%s.pdf'%matplotlib.__version__)


filenames = ( 'INSTALL', 'CHANGELOG', 'API_CHANGES', 'MIGRATION.txt')
for fname in filenames:
    oldname = os.path.join(MPL_SRC,fname)
    print 'copying %s to %s' % (oldname, fname)
    shutil.copy(oldname, fname)
shutil.copy(os.path.join(MPL_SRC, 'lib', 'matplotlib', 'mpl-data', 'matplotlibrc'), 'matplotlibrc')

# auto-generate the license file with the right version number
fmt = file('license.fmt').read()
d = {'version':matplotlib.__version__}
print >> file('license.html.template','w'), fmt%d


print 'Making screenshots'
os.system('cd screenshots; python makeshots.py; rm -f _tmp*.py')

print 'Making tutorial images'
os.system('cd tut; python runall.py')

print 'Running process_docs'
os.system('python process_docs.py')

print 'Running convert'
os.system('python convert.py')

print 'Building archive'
version = matplotlib.__version__
tarcommand = 'tar cfz site.tar.gz *.html api.pdf users_guide_%(version)s.pdf matplotlib_examples_%(version)s.zip screenshots tut doc examples matplotlibrc CHANGELOG  API_CHANGES MIGRATION.txt set_begone.py logo2.py logo2.png logo_sidebar.png basemap_readme.txt  -X exclude.txt'%locals()
print tarcommand
os.system(tarcommand)
