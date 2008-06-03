from __future__ import division
import math
import matplotlib.numerix as nx
from matplotlib.axes import Axes

_axes_sizer_elements = {}
_sizer_flags = ['left','right','bottom','top','all',
                'expand',
                'align_centre',
                'align_centre_vertical',
                'align_centre_horizontal',
                'align_right',
                'align_bottom',
                ]

def as_sizer_element(ax,**kwargs):
    if ax in _axes_sizer_elements:
        el = _axes_sizer_elements[ax]
        return el

    if isinstance(ax,Axes):
        el = MplAxesSizerElement(ax,**kwargs)
        _axes_sizer_elements[ax] = el # allow warning when adding twice
        return el

    else:
        raise ValueError("")

class MplSizerElement:
    """encapsulates anything that can be an element in a sizer"""
    def __init__(self,**kwargs):
        self.option = 0 # "weight" along sizer direction
        self.flag = {}
        self.border = 0 # in inches
        self.minsize = (1.0,1.0) # width, height in inches
        self.name = ''
        self._border_rect = None
        self._rect = None
        self._update_sizer_element_kwargs(**kwargs)
    def _update_sizer_element_kwargs(self,**kwargs):
        for key,value in kwargs.iteritems():
            if key in ['option','border','minsize','name']:
                setattr(self,key,value)
            elif key in _sizer_flags:
                self.flag[key]=value
            else:
                raise ValueError('key "%s" is not understood'%key) # hint: try centre instead of center
        self.Update() # update self.minsize and self.minsize_bordered

    def _show_contents(self,indent=0):
        buf = (' '*indent)+'MplSizerElement\n'
        return buf

    def Update(self):
        # updates self.minsize and self.minsize_bordered

        left = self.flag.get('left',False) or self.flag.get('all',False)
        right = self.flag.get('right',False) or self.flag.get('all',False)
        bottom = self.flag.get('bottom',False) or self.flag.get('all',False)
        top = self.flag.get('top',False) or self.flag.get('all',False)

        hborder = 0
        vborder = 0
        if left: hborder += self.border
        if right: hborder += self.border
        if bottom: vborder += self.border
        if top: vborder += self.border

        # self.minsize already set
        self.minsize_bordered = [self.minsize[0]+hborder,
                                 self.minsize[1]+vborder]

        if 0:
            print self.name,'MplSizerElement.Update() setting minsize_bordered',self.minsize_bordered
            print self.name,'MplSizerElement.Update() setting minsize',self.minsize
            print
        return

    def _layout(self,lbrt_inch,fig_w_inch,fig_h_inch,eps=1e-10):
        #print 'MplSizerElement._layout',self,self.name,lbrt_inch

        # check if we have to request larger size
        # check size allocation, which must include room for this element's borders
        request_w_inch = None
        request_h_inch = None
        if self.minsize_bordered[0]-eps > (lbrt_inch[2]-lbrt_inch[0]):
            request_w_inch = self.minsize_bordered[0]
##            print 'self.minsize_bordered[0]',repr(self.minsize_bordered[0])
##            print '(lbrt_inch[2]-lbrt_inch[0])',repr((lbrt_inch[2]-lbrt_inch[0]))
##            print 'requesting width increase',self,self.name,request_w_inch
##            print
        if self.minsize_bordered[1]-eps > (lbrt_inch[3]-lbrt_inch[1]):
            request_h_inch = self.minsize_bordered[1]
#            print 'requesting height increase',self,self.name,request_h_inch
        if (request_w_inch is not None) or (request_h_inch is not None):
            return request_w_inch, request_h_inch

        w_inch = lbrt_inch[2]-lbrt_inch[0]
        h_inch = lbrt_inch[3]-lbrt_inch[1]
        self._border_rect = (lbrt_inch[0]/fig_w_inch,      lbrt_inch[1]/fig_h_inch,
                             w_inch/fig_w_inch, h_inch/fig_h_inch )

        # remove border sizes
        l,b,r,t = lbrt_inch
        left = self.flag.get('left',False) or self.flag.get('all',False)
        right = self.flag.get('right',False) or self.flag.get('all',False)
        bottom = self.flag.get('bottom',False) or self.flag.get('all',False)
        top = self.flag.get('top',False) or self.flag.get('all',False)
        if left: l+=self.border
        if bottom: b+=self.border
        if right: r-=self.border
        if top: t-=self.border
        lbrt_inch = l,b,r,t

        # calculate MPL coords
        w_inch = lbrt_inch[2]-lbrt_inch[0]
        h_inch = lbrt_inch[3]-lbrt_inch[1]
        self._rect = (lbrt_inch[0]/fig_w_inch,      lbrt_inch[1]/fig_h_inch,
                      w_inch/fig_w_inch, h_inch/fig_h_inch )

        # call derived class layout_core (where the action is)
        return self._layout_core(lbrt_inch,fig_w_inch,fig_h_inch)

    def _layout_core(self,lbrt_inch,fig_w_inch,fig_h_inch):
        # does nothing in this base class -- override for interesting behavior
        return None,None

class MplAxesSizerElement( MplSizerElement ):
    def __init__(self,ax,**kwargs):
        self.ax = ax
        MplSizerElement.__init__(self,**kwargs)
    def _show_contents(self,indent=0):
        buf = (' '*indent)+'MplAxesSizerElement: %s\n'%repr(self.ax)
        return buf
    def _layout_core(self,lbrt_inch,fig_w_inch,fig_h_inch):
        if self.ax is not None:
            self.ax.set_position(self._rect)
##            if 1:
##                print 'assigning "%s" to MPL'%self.name,self.ax,'(%.2f,%.2f,%.2f,%.2f)'%self._rect
##                print '    from:',lbrt_inch,fig_w_inch,fig_h_inch
##                print
        return None,None

class MplSizer( MplSizerElement ):
    """abstract sizer class that holds elements"""
    def __init__(self):
        self.elements = []
        MplSizerElement.__init__(self)
    def Add(self, element, **kwargs):
        if not isinstance(element,MplSizerElement):
            element = as_sizer_element(element,**kwargs)
        else:
            element._update_sizer_element_kwargs(**kwargs)
        if element in self.elements:
            raise ValueError("element already in MplSizer")
        # update
        self.elements.append( element )
        self.Update()
    def _show_contents(self,indent=0):
        buf = (' '*indent)+'MplSizer:\n'
        for el in self.elements:
            buf += el._show_contents(indent=indent+2)
        return buf

class MplBoxSizer( MplSizer ):
    """vertical or horizontal sizer"""
    def __init__(self,orientation=None):
        if orientation is None:
            orientation='vertical'
        if orientation not in ['vertical','horizontal']:
            raise ValueError("only horizontal and vertical orientations allowed")
        self.orientation = orientation
        MplSizer.__init__(self)
    def _show_contents(self,indent=0):
        buf = (' '*indent)+'MplBoxSizer:\n'
        buf += MplSizer._show_contents(self,indent+2)
        return buf

    def Update(self):
        # calculate minsize based on minsize_bordered of children
        if self.orientation.startswith('v'):
            vertical=True
        elif self.orientation.startswith('h'):
            vertical=False
        else: ValueError("only vertical and horizontal supported")

        if vertical:
            dir_idx=1
            other_idx=0
        else:
            dir_idx=0
            other_idx=1

        minsize = [0,0]
        for el in self.elements:
            el.Update() # updates minsize, may not be necessary
            dir_minsize = el.minsize_bordered[dir_idx]
            other_minsize = el.minsize_bordered[other_idx]

            minsize[dir_idx] = minsize[dir_idx] + dir_minsize
            minsize[other_idx] = max(minsize[other_idx],other_minsize)

        self.minsize = minsize
        #print self.name,'MplBoxSizer.Update() setting minsize',self.minsize
        MplSizer.Update(self) # call base class (sets self.minsize_bordered)

    def _layout_core(self,lbrt_inch,fig_w_inch,fig_h_inch):
        #print 'MplBoxSizer._layout_core',self,self.name,lbrt_inch

        if self.orientation.startswith('v'):
            vertical=True
        elif self.orientation.startswith('h'):
            vertical=False
        else: ValueError("only vertical and horizontal supported")

        if vertical:
            dir_idx = 1
            sizer_width_inch = lbrt_inch[2]-lbrt_inch[0]
        else:
            dir_idx = 0
            sizer_height_inch = lbrt_inch[3]-lbrt_inch[1]

        start = lbrt_inch[dir_idx+0]
        stop = lbrt_inch[dir_idx+2]
        dist_avail = stop-start
        total_weight = 0

        # first iteration -- find inches remaining after borders and minsizes allocated
        optioned_minimum = 0
        for el in self.elements:
            if el.option == 0:
                dist_avail -= el.minsize_bordered[dir_idx]
            else:
                # make sure we don't give less than requested
                optioned_minimum += el.minsize_bordered[dir_idx]
            total_weight += el.option

        use_option = False
        if dist_avail > optioned_minimum:
            # OK, we can allocate using expansion options
            use_option = True
            if total_weight > 0:
                dist_inc = dist_avail/total_weight
            else:
                dist_inc = None

        if vertical:
            # go top to bottom
            current_location_inch = lbrt_inch[3]
            dir = -1
        else:
            # go left to right
            current_location_inch = lbrt_inch[0]
            dir = 1

        req_w_inch = None
        req_h_inch = None

        for el in self.elements:
            #print 'self, el, el.flag',self, el, el.flag
            # calculate the bordered region and call element's ._layout()
            # the element itself must deal with removing the border
            el_lt = current_location_inch
            if (el.option > 0) and use_option:
                current_location_inch += dir*dist_inc*el.option
                #print 'boxsizer',self.name,'el %s dir=%f dist_inc=%f option=%f'%(el.name,
                #                                                                 dir,
                #                                                                 dist_inc,
                #                                                                 el.option)
            else:
                current_location_inch += dir*el.minsize_bordered[dir_idx]
            el_rb = current_location_inch

            if vertical:
                el_bottom = el_rb
                el_top = el_lt
                #print 'vert boxsizer',self.name,'el',el.name
                #print 'vert boxsizer',self.name,'el top',el_top
                #print 'vert boxsizer',self.name,'el bottom',el_bottom
                if el.flag.get('expand',False):
                    # expand horizontally
                    el_lbrt_inch = (lbrt_inch[0], el_bottom,
                                    lbrt_inch[2], el_top)
                else:
                    minwidth = el.minsize_bordered[0]
                    if (el.flag.get('align_centre_horizontal',False) or
                        el.flag.get('align_centre',False)):
                        w0 = sizer_width_inch/2-minwidth/2
                        w1 = sizer_width_inch/2+minwidth/2
                        el_lbrt_inch = (lbrt_inch[0]+w0, el_bottom,
                                        lbrt_inch[0]+w1, el_top)
                    elif el.flag.get('align_right',False):
                        #print 'aligning right!'
                        el_lbrt_inch = (lbrt_inch[2]-minwidth, el_bottom,
                                        lbrt_inch[2], el_top)
                    else:
                        el_lbrt_inch = (lbrt_inch[0], el_bottom,
                                        lbrt_inch[0]+minwidth, el_top)

            else: #horizonal
                el_left = el_lt
                el_right = el_rb
                if el.flag.get('expand',False):
                    # expand vertically
                    el_lbrt_inch = (el_left, lbrt_inch[1], el_right, lbrt_inch[3])
                else:
                    minheight = el.minsize_bordered[1]
                    if (el.flag.get('align_centre_vertical',False) or
                        el.flag.get('align_centre',False)):
                        #print 'sizer_height_inch',sizer_height_inch
                        #print 'minheight',minheight
                        h0 = sizer_height_inch/2-minheight/2
                        h1 = sizer_height_inch/2+minheight/2
                        #print 'h0',h0
                        #print 'h1',h1
                        el_lbrt_inch = (el_left, lbrt_inch[1]+h0,
                                        el_right, lbrt_inch[1]+h1)
                    elif el.flag.get('align_bottom',False):
                        el_lbrt_inch = (el_left, lbrt_inch[1],
                                        el_right, lbrt_inch[1]+minheight)
                    else:
                        el_lbrt_inch = (el_left, lbrt_inch[3]-minheight,
                                        el_right, lbrt_inch[3])
            #print 'BoxSizer',self.name,'allocating',el_lbrt_inch,'to',el.name
            this_req_w_inch, this_req_h_inch = el._layout(el_lbrt_inch,
                                                          fig_w_inch,fig_h_inch)
            req_w_inch = max(req_w_inch,this_req_w_inch)
            req_h_inch = max(req_h_inch,this_req_h_inch)
            #print 'MplBoxSizer',self,'req_w_inch, req_h_inch',req_w_inch, req_h_inch

        # call base class
        return req_w_inch, req_h_inch

class MplGridSizer( MplSizer ):
    """vertical or horizontal sizer"""
    def __init__(self,cols=2,hgap=0.0,vgap=0.0,append_horiz=True):
        self.cols = cols
        self.hgap_inch = hgap
        self.vgap_inch = vgap
        self.append_horiz = append_horiz # if true, add horizontally
        MplSizer.__init__(self)

    def _show_contents(self,indent=0):
        buf = (' '*indent)+'MplGridSizer:\n'
        buf += MplSizer._show_contents(self,indent+2)
        return buf

    def Update(self):
        # calculate minsize based on minsize_bordered of children
        maxel = [0,0]
        for el in self.elements:
            el.Update() # updates minsize, may not be necessary
            maxel[0] = max(maxel[0],el.minsize_bordered[0])
            maxel[1] = max(maxel[1],el.minsize_bordered[1])

        n_hgaps = max(0,self.cols-1)
        total_hgap = n_hgaps*self.hgap_inch
        rows = int(math.ceil(len(self.elements)/self.cols))
        n_vgaps = max(0,rows-1)
        total_vgap = n_vgaps*self.vgap_inch
        minsize0 = maxel[0]*self.cols + total_hgap
        minsize1 = maxel[1]*rows + total_vgap
        self.minsize = (minsize0,minsize1)
        #print self.name,'MplGridSizer.Update() setting minsize',self.minsize
        MplSizer.Update(self) # call base class (sets self.minsize_bordered)

    def _layout_core(self,lbrt_inch,fig_w_inch,fig_h_inch):
        #print
        #print 'MplGridSizer._layout_core',self,self.name,lbrt_inch

##        print 'len(self.elements)',len(self.elements)
##        print 'self.cols',self.cols
##        print 'len(self.elements)/self.cols',len(self.elements)/self.cols
        rows = int(math.ceil(len(self.elements)/self.cols))
##        print 'rows',rows

        n_hgaps = max(0,self.cols-1)
        total_hgap = n_hgaps*self.hgap_inch

        if self.flag.get('expand',False):
            total_width_inches = lbrt_inch[2]-lbrt_inch[0]
        else:
            total_width_inches = self.minsize[0]
        col_width = (total_width_inches-total_hgap)/self.cols
        col_stride = col_width + self.hgap_inch

        n_vgaps = max(0,rows-1)
        total_vgap = n_vgaps*self.vgap_inch

        if self.flag.get('expand',False):
            total_height_inches = lbrt_inch[3]-lbrt_inch[1]
        else:
            total_height_inches = self.minsize[1]
        row_height = (total_height_inches-total_vgap)/rows
        row_stride = row_height + self.vgap_inch

        req_w_inch = None
        req_h_inch = None

        for i in range(rows):
            y1 = lbrt_inch[3] - i*row_stride # top
            y0 = lbrt_inch[3] - i*row_stride - row_height # bottom
            #print 'i',i
            #print 'y0,y1',y0,y1
            for j in range(self.cols):
                if self.append_horiz:
                    idx = i*self.cols+j
                else:
                    idx = j*rows+i
                if idx >= len(self.elements):
                    continue

                el = self.elements[idx]

                x0 = lbrt_inch[0] + j*col_stride
                x1 = lbrt_inch[0] + j*col_stride + col_width

                if el.flag.get('expand',False):
                    el_lbrt_inch = (x0,y0,x1,y1)
                else:
                    x05 = (x0+x1)/2
                    y05 = (y0+y1)/2
                    w = el.minsize_bordered[0]
                    h = el.minsize_bordered[1]
                    w2 = w/2
                    h2 = h/2
                    if el.flag.get('align_centre',False):
                        el_lbrt_inch = (x05-w2,y05-h2,
                                        x05+w2,y05+h2)
                    elif el.flag.get('align_centre_horizontal',False):
                        el_lbrt_inch = (x05-w2,y1-h,
                                        x05+w2,y1)
                    elif el.flag.get('align_centre_vertical',False):
                        el_lbrt_inch = (x0,  y05-h2,
                                        x0+w,y05+h2)
                    # XXX more needed
                    else:
                        # top left default
                        el_lbrt_inch = (x0,  y1-h,
                                        x0+w,y1)
                #print 'el_lbrt_inch',el_lbrt_inch
                this_req_w_inch, this_req_h_inch = el._layout(el_lbrt_inch,
                                                              fig_w_inch,fig_h_inch)
                req_w_inch = max(req_w_inch,this_req_w_inch)
                req_h_inch = max(req_h_inch,this_req_h_inch)

        if req_w_inch is not None:
            req_w_inch = self.cols*req_w_inch

        if req_h_inch is not None:
            req_h_inch = rows*req_h_inch

        # call base class
        return req_w_inch, req_h_inch

class MplSizerFrame:
    def __init__(self,fig):
        self.fig = fig
        self.sizer = None
    def _show_contents(self,indent=0):
        buf =  (' '*indent)+'MplSizerFrame:\n'
        buf += self.sizer._show_contents(indent+2)
        return buf
    def SetSizer(self,sizer, **kwargs):
        """like Add but only a single sizer can be added"""
        sizer._update_sizer_element_kwargs(**kwargs)
        sizer.Update() # calculate minsize requirements
        self.sizer = sizer

    def Layout(self):
        self.sizer.Update() # calculate minsize requirements

        fig_w_inch = self.fig.get_figwidth()
        fig_h_inch = self.fig.get_figheight()
        lbrt_inch = (0,0,fig_w_inch,fig_h_inch) # bounding box within figure
        req_w_inch, req_h_inch = self.sizer._layout(lbrt_inch,fig_w_inch,fig_h_inch)
#        print '1: req_w_inch, req_h_inch',repr(req_w_inch), repr(req_h_inch)

        # this is a mini-hack to deal with floating point imprecision
        max_tries = 1
        eps=1e-8
        for ntry in range(max_tries):
            if (req_w_inch is not None) or (req_h_inch is not None):
                # request was made to enlarge the figure
                if req_w_inch is not None:
                    self.fig.set_figwidth(req_w_inch+ntry*eps)
                if req_h_inch is not None:
                    self.fig.set_figheight(req_h_inch+ntry*eps)

                fig_w_inch = self.fig.get_figwidth()
##                print 'fig_w_inch',fig_w_inch
                fig_h_inch = self.fig.get_figheight()
##                print 'fig_h_inch',fig_h_inch
                lbrt_inch = (0,0,fig_w_inch,fig_h_inch) # bounding box within figure

                req_w_inch, req_h_inch = self.sizer._layout(lbrt_inch,fig_w_inch,fig_h_inch)
##                print 'ntry %d: req_w_inch, req_h_inch'%(ntry,),repr(req_w_inch), repr(req_h_inch)
        if (req_w_inch is not None) or (req_h_inch is not None):
            raise RuntimeError('failed to layout')

