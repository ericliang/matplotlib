modules = (
    'matplotlib.afm',
    'matplotlib.artist',
    'matplotlib.axis',
    'matplotlib.axes',
    'matplotlib.backend_bases',
    'matplotlib.backends.backend_agg',
    'matplotlib.backends.backend_cairo',
    'matplotlib.backends.backend_fltkagg',
    'matplotlib.backends.backend_gtkcairo',
    'matplotlib.backends.backend_gtk',
    'matplotlib.backends.backend_gtkagg',
    'matplotlib.backends.backend_ps',
    'matplotlib.backends.backend_svg',
    'matplotlib.backends.backend_template',
    'matplotlib.backends.backend_tkagg',
    'matplotlib.backends.backend_qt',
    'matplotlib.backends.backend_qtagg',
    'matplotlib.backends.backend_wx',
    'matplotlib.backends.backend_wxagg',
    'matplotlib.cbook',
    'matplotlib.cm',
    'matplotlib.collections',
    'matplotlib.colorbar',
    'matplotlib.colors',
    'matplotlib.contour',
    'matplotlib.dates',
    'matplotlib.dviread',
    'matplotlib.figure',
    'matplotlib.finance',
    'matplotlib.font_manager',
    'matplotlib.fontconfig_pattern',
    'matplotlib.ft2font',
    'matplotlib.image',
    'matplotlib.legend',
    'matplotlib.lines',
    'matplotlib.mathtext',
    'matplotlib.mlab',
    'matplotlib.mpl',    
    'matplotlib.numerix',
    'matplotlib.patches',
    'matplotlib.path',    
    'matplotlib.pylab',
    'matplotlib.pyplot',
    'matplotlib.quiver',
    'matplotlib.rcsetup',
    'matplotlib.scale',    
    'matplotlib.table',
    'matplotlib.texmanager',
    'matplotlib.text',
    'matplotlib.ticker',
    'mpl_toolkits.basemap',
    'mpl_toolkits.exceltools',
    'mpl_toolkits.gtktools',        
    'mpl_toolkits.natgrid',
    'matplotlib.transforms',
    'matplotlib.type1font',
    'matplotlib.units',
    'matplotlib.widgets',
    )


def get_mpl_commands():
    """
    return value is a list of (header, commands) where commands is a
    list of (func, desc)
    """
    import matplotlib.pylab
    plot_commands = []
    # parse the header for the commands provided commands
    import inspect
    these = []
    for line in inspect.getsourcelines(matplotlib.pylab)[0]:
        line = line.strip()
        if not len(line): continue
        if line.startswith('__end'): break
        if line.startswith('_'):
            header = line[1:].strip()
            these = []
            plot_commands.append((header, these))
            continue
        tup = line.split('-', 1)
        if len(tup)!=2: continue
        func, desc = tup
        func = func.strip()
        desc = desc.strip()
        these.append((func, desc))
    return plot_commands
