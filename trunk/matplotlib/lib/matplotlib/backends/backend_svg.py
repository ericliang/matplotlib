from __future__ import division

import os, codecs, base64, tempfile, urllib

from matplotlib import verbose, __version__, rcParams
from matplotlib.backend_bases import RendererBase, GraphicsContextBase,\
     FigureManagerBase, FigureCanvasBase
from matplotlib.colors import rgb2hex
from matplotlib.figure import Figure
from matplotlib.font_manager import fontManager, FontProperties
from matplotlib.ft2font import FT2Font, KERNING_UNFITTED, KERNING_DEFAULT, KERNING_UNSCALED
from matplotlib.mathtext import math_parse_s_ft2font_svg

backend_version = __version__

def new_figure_manager(num, *args, **kwargs):
    FigureClass = kwargs.pop('FigureClass', Figure)
    thisFig = FigureClass(*args)
    canvas  = FigureCanvasSVG(thisFig)
    manager = FigureManagerSVG(canvas, num)
    return manager


_fontd = {}
_capstyle_d = {'projecting' : 'square', 'butt' : 'butt', 'round': 'round',}
class RendererSVG(RendererBase):
    FONT_SCALE = 1200.0

    def __init__(self, width, height, svgwriter, basename=None):
        self.width=width
        self.height=height
        self._svgwriter = svgwriter

        self._groupd = {}
        if not rcParams['svg.image_inline']:
            assert basename is not None
            self.basename = basename
            self._imaged = {}
        self._clipd = {}
        self._char_defs = {}
        svgwriter.write(svgProlog%(width,height,width,height))

    def _draw_svg_element(self, element, details, gc, rgbFace):
        cliprect, clipid = self._get_gc_clip_svg(gc)
        if clipid is None:
            clippath = ''
        else:
            clippath = 'clip-path="url(#%s)"' % clipid

        self._svgwriter.write ('%s<%s %s %s %s/>\n' % (
            cliprect,
            element, self._get_style(gc, rgbFace), clippath, details))

    def _get_font(self, prop):
        key = hash(prop)
        font = _fontd.get(key)
        if font is None:
            fname = fontManager.findfont(prop)
            font = FT2Font(str(fname))
            _fontd[key] = font
        font.clear()
        size = prop.get_size_in_points()
        font.set_size(size, 72.0)
        return font

    def _get_style(self, gc, rgbFace):
        """
        return the style string.
        style is generated from the GraphicsContext, rgbFace and clippath
        """
        if rgbFace is None:
            fill = 'none'
        else:
            fill = rgb2hex(rgbFace)

        offset, seq = gc.get_dashes()
        if seq is None:
            dashes = ''
        else:
            dashes = 'stroke-dasharray: %s; stroke-dashoffset: %f;' % (
                ' '.join(['%f'%val for val in seq]), offset)

        linewidth = gc.get_linewidth()
        if linewidth:
            return 'style="fill: %s; stroke: %s; stroke-width: %f; ' \
                'stroke-linejoin: %s; stroke-linecap: %s; %s opacity: %f"' % (
                         fill,
                         rgb2hex(gc.get_rgb()),
                         linewidth,
                         gc.get_joinstyle(),
                         _capstyle_d[gc.get_capstyle()],
                         dashes,
                         gc.get_alpha(),
                )
        else:
            return 'style="fill: %s; opacity: %f"' % (\
                         fill,
                         gc.get_alpha(),
                )

    def _get_gc_clip_svg(self, gc):
        cliprect = gc.get_clip_rectangle()
        if cliprect is None:
            return '', None
        else:
            # See if we've already seen this clip rectangle
            key = hash(cliprect)
            if self._clipd.get(key) is None:  # If not, store a new clipPath
                self._clipd[key] = cliprect
                x, y, w, h = cliprect
                y = self.height-(y+h)
                box = """\
<defs>
    <clipPath id="%(key)s">
    <rect x="%(x)f" y="%(y)f" width="%(w)f" height="%(h)f"
    style="stroke: gray; fill: none;"/>
    </clipPath>
</defs>
""" % locals()
                return box, key
            else:
                # return id of previously defined clipPath
                return '', key

    def open_group(self, s):
        self._groupd[s] = self._groupd.get(s,0) + 1
        self._svgwriter.write('<g id="%s%d">\n' % (s, self._groupd[s]))

    def close_group(self, s):
        self._svgwriter.write('</g>\n')

    def draw_arc(self, gc, rgbFace, x, y, width, height, angle1, angle2, rotation):
        """
        Ignores angles for now
        """
        details = 'cx="%f" cy="%f" rx="%f" ry="%f" transform="rotate(%f %f %f)"' % \
            (x,  self.height-y, width/2.0, height/2.0, -rotation, x, self.height-y)
        self._draw_svg_element('ellipse', details, gc, rgbFace)

    def option_image_nocomposite(self):
        """
        if svg.image_noscale is True, compositing multiple images into one is prohibited
        """
        return rcParams['svg.image_noscale']

    def draw_image(self, x, y, im, bbox):
        trans = [1,0,0,1,0,0]
        transstr = ''
        if rcParams['svg.image_noscale']:
            trans = list(im.get_matrix())
            if im.get_interpolation() != 0:
                trans[4] += trans[0]
                trans[5] += trans[3]
            trans[5] = -trans[5]
            transstr = 'transform="matrix(%f %f %f %f %f %f)" '%tuple(trans)
            assert trans[1] == 0
            assert trans[2] == 0
            numrows,numcols = im.get_size()
            im.reset_matrix()
            im.set_interpolation(0)
            im.resize(numcols, numrows)

        h,w = im.get_size_out()

        if rcParams['svg.image_inline']:
            filename = os.path.join (tempfile.gettempdir(),
                                    tempfile.gettempprefix() + '.png'
                                    )

            verbose.report ('Writing temporary image file for inlining: %s' % filename)
            # im.write_png() accepts a filename, not file object, would be
            # good to avoid using files and write to mem with StringIO

            # JDH: it *would* be good, but I don't know how to do this
            # since libpng seems to want a FILE* and StringIO doesn't seem
            # to provide one.  I suspect there is a way, but I don't know
            # it

            im.flipud_out()
            im.write_png(filename)
            im.flipud_out()

            imfile = file (filename, 'r')
            image64 = base64.encodestring (imfile.read())
            imfile.close()
            os.remove(filename)
            hrefstr = 'data:image/png;base64,\n' + image64

        else:
            self._imaged[self.basename] = self._imaged.get(self.basename,0) + 1
            filename = '%s.image%d.png'%(self.basename, self._imaged[self.basename])
            verbose.report( 'Writing image file for inclusion: %s' % filename)
            im.flipud_out()
            im.write_png(filename)
            im.flipud_out()
            hrefstr = filename

        self._svgwriter.write (
            '<image x="%f" y="%f" width="%f" height="%f" '
            'xlink:href="%s" %s/>\n'%(x/trans[0], (self.height-y)/trans[3]-h, w, h, hrefstr, transstr)
            )

    def draw_line(self, gc, x1, y1, x2, y2):
        details = 'd="M %f,%f L %f,%f"' % (x1, self.height-y1,
                                           x2, self.height-y2)
        self._draw_svg_element('path', details, gc, None)

    def draw_lines(self, gc, x, y, transform=None):
        if len(x)==0: return
        if len(x)!=len(y):
            raise ValueError('x and y must be the same length')

        y = self.height - y
        details = ['d="M %f,%f' % (x[0], y[0])]
        xys = zip(x[1:], y[1:])
        details.extend(['L %f,%f' % tup for tup in xys])
        details.append('"')
        details = ' '.join(details)
        self._draw_svg_element('path', details, gc, None)

    def draw_point(self, gc, x, y):
        # result seems to have a hole in it...
        self.draw_arc(gc, gc.get_rgb(), x, y, 1, 0, 0, 0, 0)

    def draw_polygon(self, gc, rgbFace, points):
        details = 'points = "%s"' % ' '.join(['%f,%f'%(x,self.height-y)
                                              for x, y in points])
        self._draw_svg_element('polygon', details, gc, rgbFace)

    def draw_rectangle(self, gc, rgbFace, x, y, width, height):
        details = 'width="%f" height="%f" x="%f" y="%f"' % (width, height, x,
                                                         self.height-y-height)
        self._draw_svg_element('rect', details, gc, rgbFace)

    def draw_text(self, gc, x, y, s, prop, angle, ismath):
        if ismath:
            self._draw_mathtext(gc, x, y, s, prop, angle)
            return

        font = self._get_font(prop)

        thetext = '%s' % s
        fontfamily = font.family_name
        fontstyle = font.style_name
        fontsize = prop.get_size_in_points()
        color = rgb2hex(gc.get_rgb())

        if rcParams['svg.embed_char_paths']:
            svg = '<g transform="'
            if angle!=0:
                svg += 'translate(%f,%f) rotate(%1.1f) ' % (x,y,-angle) # Inkscape doesn't support rotate(angle x y)
            else:
                svg += 'translate(%f,%f)' % (x,y)
            svg += ' scale(%f)">\n' % (fontsize / self.FONT_SCALE)

            cmap = font.get_charmap()
            lastgind = None
            currx = 0
            for c in s:
                charid = self._add_char_def(prop, c)
                ccode = ord(c)
                gind = cmap.get(ccode)
                if gind is None:
                    ccode = ord('?')
                    gind = 0
                glyph = font.load_char(ccode)

                if lastgind is not None:
                    kern = font.get_kerning(lastgind, gind, KERNING_UNFITTED)
                else:
                    kern = 0
                lastgind = gind
                currx += kern/64.0

                svg += ('<use xlink:href="#%s" transform="translate(%s)"/>\n' 
                         % (charid, currx / (fontsize / self.FONT_SCALE)))
                
                currx += glyph.linearHoriAdvance / 65536.0
            svg += '</g>\n'
        else:
            style = 'font-size: %f; font-family: %s; font-style: %s; fill: %s;'%(fontsize, fontfamily,fontstyle, color)
            if angle!=0:
                transform = 'transform="translate(%f,%f) rotate(%1.1f) translate(%f,%f)"' % (x,y,-angle,-x,-y) # Inkscape doesn't support rotate(angle x y)
            else: transform = ''

            svg = """\
<text style="%(style)s" x="%(x)f" y="%(y)f" %(transform)s>%(thetext)s</text>
""" % locals()
        self._svgwriter.write (svg)

    def _add_char_def(self, prop, char):
        newprop = prop.copy()
        newprop.set_size(self.FONT_SCALE)
        font = self._get_font(newprop)
        ps_name = font.get_sfnt()[(1,0,0,6)]
        id = urllib.quote('%s-%d' % (ps_name, ord(char)))
        if id in self._char_defs:
            return id

        path_element = '<path id="%s" ' % (id)
        path_data = []
        glyph = font.load_char(ord(char))
        currx, curry = 0.0, 0.0
        for step in glyph.path:
            if step[0] == 0:   # MOVE_TO
                path_data.append("m%s %s" % 
                                 (step[1] - currx, -step[2] - curry))
            elif step[0] == 1: # LINE_TO
                path_data.append("l%s %s" % 
                                 (step[1] - currx, -step[2] - curry))
            elif step[0] == 2: # CURVE3
                path_data.append("q%s %s %s %s" % 
                                 (step[1] - currx, -step[2] - curry,
                                  step[3] - currx, -step[4] - curry))
            elif step[0] == 3: # CURVE4
                path_data.append("c%s %s %s %s %s %s" % 
                                 (step[1] - currx, -step[2] - curry,
                                  step[3] - currx, -step[4] - curry,
                                  step[5] - currx, -step[6] - curry))
            elif step[0] == 4: # ENDPOLY
                path_data.append("Z")

            if step[0] != 4:
                currx, curry = step[-2], -step[-1]
        path_element += 'd="%s"/>\n' % " ".join(path_data)
        
        self._char_defs[id] = path_element
        return id

    def _draw_mathtext(self, gc, x, y, s, prop, angle):
        """
        Draw math text using matplotlib.mathtext
        """
        fontsize = prop.get_size_in_points()
        width, height, svg_elements = math_parse_s_ft2font_svg(s, 72, fontsize)
        svg_glyphs = svg_elements.svg_glyphs
        svg_lines = svg_elements.svg_lines
        color = rgb2hex(gc.get_rgb())

        self.open_group("mathtext")

        if rcParams['svg.embed_char_paths']:
            svg = '<g style="fill: %s" transform="' % color
            if angle != 0:
                svg += ( 'translate(%f,%f) rotate(%1.1f)'
                         % (x,y,-angle) ) 
            else:
                svg += 'translate(%f,%f)' % (x, y)
            svg += '">\n'

            for fontname, fontsize, thetext, new_x, new_y_mtc, metrics in svg_glyphs:
                prop = FontProperties(family=fontname, size=fontsize)
                charid = self._add_char_def(prop, thetext)

                svg += '<use xlink:href="#%s" transform="translate(%s, %s) scale(%s)"/>\n' % (charid, new_x, -new_y_mtc, fontsize / self.FONT_SCALE)
            svg += '</g>\n'
        else: # not rcParams['svg.embed_char_paths']
            svg = '<text style="fill: %s" x="%f" y="%f"' % (color,x,y)

            if angle != 0:
                svg += ( ' transform="translate(%f,%f) rotate(%1.1f) translate(%f,%f)"'
                         % (x,y,-angle,-x,-y) ) # Inkscape doesn't support rotate(angle x y)
            svg += '>\n'

            curr_x,curr_y = 0.0,0.0

            for fontname, fontsize, thetext, new_x, new_y_mtc, metrics in svg_glyphs:
                if rcParams["mathtext.mathtext2"]:
                    new_y = new_y_mtc - height
                else:
                    new_y = - new_y_mtc

                svg += '<tspan'
                svg += ' style="font-size: %f; font-family: %s"'%(fontsize, fontname)
                xadvance = metrics.advance
                svg += ' textLength="%f"' % xadvance

                dx = new_x - curr_x
                if dx != 0.0:
                    svg += ' dx="%f"' % dx

                dy = new_y - curr_y
                if dy != 0.0:
                    svg += ' dy="%f"' % dy

                svg += '>%s</tspan>\n' % thetext

                curr_x = new_x + xadvance
                curr_y = new_y

            svg += '</text>\n'

        self._svgwriter.write (svg)
        rgbFace = gc.get_rgb()
        for xmin, ymin, xmax, ymax in svg_lines:
            newx, newy = x + xmin, y + height - ymax#-(ymax-ymin)/2#-height
            self.draw_rectangle(gc, rgbFace, newx, newy, xmax-xmin, ymax-ymin)
            #~ self.draw_line(gc, x + xmin, y + ymin,# - height,
                                     #~ x + xmax, y + ymax)# - height)
        self.close_group("mathtext")

    def finish(self):
        if len(self._char_defs):
            self._svgwriter.write('<defs id="fontpaths">\n')
            for path in self._char_defs.values():
                self._svgwriter.write(path)
            self._svgwriter.write('</defs>\n')
        self._svgwriter.write('</svg>\n')

    def flipy(self):
        return True

    def get_canvas_width_height(self):
        return self.width, self.height

    def get_text_width_height(self, s, prop, ismath):
        if ismath:
            width, height, trash = math_parse_s_ft2font_svg(
                s, 72, prop.get_size_in_points())
            return width, height
        font = self._get_font(prop)
        font.set_text(s, 0.0)
        w, h = font.get_width_height()
        w /= 64.0  # convert from subpixels
        h /= 64.0
        return w, h


class FigureCanvasSVG(FigureCanvasBase):

    def print_figure(self, filename, dpi, facecolor='w', edgecolor='w',
                     orientation='portrait', **kwargs):
        # save figure settings
        origDPI       = self.figure.dpi.get()
        origfacecolor = self.figure.get_facecolor()
        origedgecolor = self.figure.get_edgecolor()

        self.figure.dpi.set(72)
        self.figure.set_facecolor(facecolor)
        self.figure.set_edgecolor(edgecolor)
        width, height = self.figure.get_size_inches()
        w, h = width*72, height*72

        basename, ext = os.path.splitext(filename)
        if not len(ext): filename += '.svg'
        svgwriter = codecs.open( filename, 'w', 'utf-8' )
        renderer = RendererSVG(w, h, svgwriter, basename)
        self.figure.draw(renderer)
        renderer.finish()

        # restore figure settings
        self.figure.dpi.set(origDPI)
        self.figure.set_facecolor(origfacecolor)
        self.figure.set_edgecolor(origedgecolor)
        svgwriter.close()

class FigureManagerSVG(FigureManagerBase):
    pass

FigureManager = FigureManagerSVG

svgProlog = """\
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<!-- Created with matplotlib (http://matplotlib.sourceforge.net/) -->
<svg width="%i" height="%i" viewBox="0 0 %i %i"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:xlink="http://www.w3.org/1999/xlink"
   version="1.1"
   id="svg1">
"""
