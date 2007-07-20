r"""

OVERVIEW

  mathtext is a module for parsing TeX expressions and drawing them
  into a matplotlib.ft2font image buffer.  You can draw from this
  buffer into your backend.

  A large set of the TeX symbols are provided (see below).
  Subscripting and superscripting are supported, as well as the
  over/under style of subscripting with \sum, \int, etc.

  The module uses pyparsing to parse the TeX expression, an so can
  handle fairly complex TeX expressions Eg, the following renders
  correctly

  s = r'$\cal{R}\prod_{i=\alpha\cal{B}}^\infty a_i\rm{sin}(2 \pi f x_i)$'

  The fonts \cal, \rm, \it, and \tt are allowed.

  The following accents are provided: \hat, \breve, \grave, \bar,
  \acute, \tilde, \vec, \dot, \ddot.  All of them have the same
  syntax, eg to make an overbar you do \bar{o} or to make an o umlaut
  you do \ddot{o}.  The shortcuts are also provided, eg: \"o \'e \`e
  \~n \.x \^y

  The spacing elements \ , \/ and \hspace{num} are provided.  \/
  inserts a small space, and \hspace{num} inserts a fraction of the
  current fontsize.  Eg, if num=0.5 and the fontsize is 12.0,
  hspace{0.5} inserts 6 points of space



  If you find TeX expressions that don't parse or render properly,
  please email me, but please check KNOWN ISSUES below first.

REQUIREMENTS

  mathtext requires matplotlib.ft2font.  Set BUILD_FT2FONT=True in
  setup.py.  See BACKENDS below for a summary of availability by
  backend.

LICENSING:

  The computer modern fonts this package uses are part of the BaKoMa
  fonts, which are (now) free for commercial and noncommercial use and
  redistribution; see license/LICENSE_BAKOMA in the matplotlib src
  distribution for redistribution requirements.

USAGE:

  See http://matplotlib.sourceforge.net/tutorial.html#mathtext for a
  tutorial introduction.

  Any text element (xlabel, ylabel, title, text, etc) can use TeX
  markup, as in

    xlabel(r'$\Delta_i$')
           ^
        use raw strings

  The $ symbols must be the first and last symbols in the string.  Eg,
  you cannot do

    r'My label $x_i$'.

  but you can change fonts, as in

    r'$\rm{My label} x_i$'

  to achieve the same effect.

  A large set of the TeX symbols are provided.  Subscripting and
  superscripting are supported, as well as the over/under style of
  subscripting with \sum, \int, etc.


  Allowed TeX symbols:

  \/ \Delta \Downarrow \Gamma \Im \LEFTangle \LEFTbrace \LEFTbracket
  \LEFTparen \Lambda \Leftarrow \Leftbrace \Leftbracket \Leftparen
  \Leftrightarrow \Omega \P \Phi \Pi \Psi \RIGHTangle \RIGHTbrace
  \RIGHTbracket \RIGHTparen \Re \Rightarrow \Rightbrace \Rightbracket
  \Rightparen \S \SQRT \Sigma \Sqrt \Theta \Uparrow \Updownarrow
  \Upsilon \Vert \Xi \aleph \alpha \approx \angstrom \ast \asymp
  \backslash \beta \bigcap \bigcirc \bigcup \bigodot \bigoplus
  \bigotimes \bigtriangledown \bigtriangleup \biguplus \bigvee
  \bigwedge \bot \bullet \cap \cdot \chi \circ \clubsuit \coprod \cup
  \dag \dashv \ddag \delta \diamond \diamondsuit \div \downarrow \ell
  \emptyset \epsilon \equiv \eta \exists \flat \forall \frown \gamma
  \geq \gg \heartsuit \hspace \imath \in \infty \int \iota \jmath
  \kappa \lambda \langle \lbrace \lceil \leftangle \leftarrow
  \leftbrace \leftbracket \leftharpoondown \leftharpoonup \leftparen
  \leftrightarrow \leq \lfloor \ll \mid \mp \mu \nabla \natural
  \nearrow \neg \ni \nu \nwarrow \odot \oint \omega \ominus \oplus
  \oslash \otimes \phi \pi \pm \prec \preceq \prime \prod \propto \psi
  \rangle \rbrace \rceil \rfloor \rho \rightangle \rightarrow
  \rightbrace \rightbracket \rightharpoondown \rightharpoonup
  \rightparen \searrow \sharp \sigma \sim \simeq \slash \smile
  \spadesuit \sqcap \sqcup \sqrt \sqsubseteq \sqsupseteq \subset
  \subseteq \succ \succeq \sum \supset \supseteq \swarrow \tau \theta
  \times \top \triangleleft \triangleright \uparrow \updownarrow
  \uplus \upsilon \varepsilon \varphi \varphi \varrho \varsigma
  \vartheta \vdash \vee \vert \wedge \wp \wr \xi \zeta


BACKENDS

  mathtext currently works with GTK, Agg, GTKAgg, TkAgg and WxAgg and
  PS, though only horizontal and vertical rotations are supported in
  *Agg

  mathtext now embeds the TrueType computer modern fonts into the PS
  file, so what you see on the screen should be what you get on paper.

  Backends which don't support mathtext will just render the TeX
  string as a literal.  Stay tuned.


KNOWN ISSUES:

 - I would also like to add a few more layout commands, like \frac.

STATUS:
  The *Unicode* classes were incomplete when I found them, and have
  not been refactored to support intermingling of regular text and
  math text yet.  They are most likely broken. -- Michael Droettboom, July 2007
 
Author    : John Hunter <jdhunter@ace.bsd.uchicago.edu>
            Michael Droettboom <mdroe@stsci.edu> (rewrite based on TeX algorithms)
Copyright : John Hunter (2004,2005)
License   : matplotlib license (PSF compatible)

"""
from __future__ import division
import os, sys
from cStringIO import StringIO
from sets import Set
from warnings import warn

from matplotlib import verbose
from matplotlib.pyparsing import Literal, Word, OneOrMore, ZeroOrMore, \
     Combine, Group, Optional, Forward, NotAny, alphas, nums, alphanums, \
     StringStart, StringEnd, ParseException, FollowedBy, Regex, \
     operatorPrecedence, opAssoc, ParseResults, Or, Suppress, oneOf

from matplotlib.afm import AFM
from matplotlib.cbook import enumerate, iterable, Bunch, get_realpath_and_stat
from matplotlib.ft2font import FT2Font
from matplotlib.font_manager import fontManager, FontProperties
from matplotlib._mathtext_data import latex_to_bakoma, cmkern, \
        latex_to_standard, tex2uni, type12uni, tex2type1, uni2type1
from matplotlib.numerix import absolute
from matplotlib import get_data_path, rcParams

# symbols that have the sub and superscripts over/under
overunder_symbols = {
    r'\sum'    : 1,
    r'\int'    : 1,
    r'\prod'   : 1,
    r'\coprod' : 1,
    }
# a character over another character
charOverChars = {
    # The first 2 entires in the tuple are (font, char, sizescale) for
    # the two symbols under and over.  The third entry is the space
    # between the two symbols in points
    r'\angstrom' : (  ('rm', 'A', 1.0), (None, '\circ', 0.5), 0.0 ),
    }

##############################################################################
# FONTS

def font_open(filename):
    ext = filename.rsplit('.',1)[1]
    if ext == 'afm':
        return AFM(str(filename))
    else:
        return FT2Font(str(filename))


def get_unicode_index(symbol):
    """get_unicode_index(symbol) -> integer

Return the integer index (from the Unicode table) of symbol.
symbol can be a single unicode character, a TeX command (i.e. r'\pi'),
or a Type1 symbol name (i.e. 'phi').

"""
    try:# This will succeed if symbol is a single unicode char
        return ord(symbol)
    except TypeError:
        pass
    try:# Is symbol a TeX symbol (i.e. \alpha)
        return tex2uni[symbol.strip("\\")]
    except KeyError:
        pass
    try:# Is symbol a Type1 name (i.e. degree)? If not raise error
        return type12uni[symbol]
    except KeyError:
        message = """'%(symbol)s' is not a valid Unicode character or
TeX/Type1 symbol"""%locals()
        raise ValueError, message


#Not used, but might turn useful
def get_type1_name(symbol):
    """get_type1_name(symbol) -> string

Returns the the Type1 name of symbol.
symbol can be a single unicode character, or a TeX command (i.e. r'\pi').

"""
    try:# This will succeed if symbol is a single unicode char
        return uni2type1[ord(symbol)]
    except TypeError:
        pass
    try:# Is symbol a TeX symbol (i.e. \alpha)
        return tex2type1[symbol.strip("\\")]
    except KeyError:
        pass
    # The symbol is already a Type1 name so return it
    if isinstance(symbol, str):
        return symbol
    else:
        # The user did not suply a valid symbol, show usage
        raise ValueError, get_type1_name.__doc__


class Fonts:
    """
    An abstract base class for fonts that want to render mathtext

    The class must be able to take symbol keys and font file names and
    return the character metrics as well as do the drawing
    """
    
    def get_kern(self, facename, symleft, symright, fontsize, dpi):
        """
        Get the kerning distance for font between symleft and symright.

        facename is one of tt, it, rm, cal or None

        sym is a single symbol(alphanum, punct) or a special symbol
        like \sigma.

        """
        return 0

    def get_metrics(self, facename, sym, fontsize, dpi):
        """
        facename is one of tt, it, rm, cal or None

        sym is a single symbol(alphanum, punct) or a special symbol
        like \sigma.

        fontsize is in points

        Return object has attributes - see
        http://www.freetype.org/freetype2/docs/tutorial/step2.html for
        a pictoral representation of these attributes

          advance
          height
          width
          xmin, xmax, ymin, ymax  - the ink rectangle of the glyph
          """
        raise NotImplementedError('Derived must override')

    def set_canvas_size(self, w, h):
        'Dimension the drawing canvas; may be a noop'
        self.width, self.height = w, h

    def render(self, ox, oy, facename, sym, fontsize, dpi):
        pass

    def render_rect_filled(self, x1, y1, x2, y2):
        pass
        
    def get_used_characters(self):
        return {}
    
    
class DummyFonts(Fonts):
    'dummy class for debugging parser'
    def get_metrics(self, font, sym, fontsize, dpi):

        metrics = Bunch(
            advance  = 0,
            height   = 0,
            width    = 0,
            xmin = 0,
            xmax = 0,
            ymin = 0,
            ymax = 0,
            )
        return metrics


class UnicodeFonts(Fonts):
    """An abstract base class for handling Unicode fonts.

Specific terminology:
 * fontface: an FT2Font object, corresponding to a facename
 * facename: a string that defines the (type)face's name - 'rm', 'it' etc.
 * filename: a string that is used for generating a fontface object
 * symbol*: a single Unicode character or a TeX command,
    or to be precise, a TeX symbol command like \alpha (but not \frac) or
    even a Type1/PS name
 * filenamesd: a dict that maps the face's name to the filename:
    filenamesd = { 'cal' : 'fontnamecal.ext',
                  'rm'  : 'fontnamerm.ext',
                  'tt'  : 'fontnamett.ext',
                  'it'  : 'fontnameit.ext',
                  None  : 'fontnamesmth.ext'}
    filenamesd should be declared as a class atribute
 * glyphdict: a dict used for caching of glyph specific data
 * fonts: a dict of facename -> fontface pairs
 * charmaps: a dict of facename -> charmap pairs. Charmap maps character
   codes to glyph indices
 * glyphmaps: a dict of facename -> glyphmap pairs. A glyphmap is an
    inverted charmap
 * output: a string in ['Agg','SVG','PS'], coresponding to the backends
 * index: Fontfile specific index of a glyph.

"""

    # The path to the dir with the fontfiles
    def __init__(self, output='Agg'):
        self.facenames = self.filenamesd.keys()
        # Set the filenames to full path
        for facename in self.filenamesd:
            self.filenamesd[facename] = self.filenamesd[facename]
        if output:
            self.output = output
        # self.glyphdict[key] = facename, metrics, glyph, offset
        self.glyphdict = {}

        self.fonts = dict(
            [ (facename, font_open(self.filenamesd[facename])) for
                    facename in self.facenames])
        # a dict of charcode -> glyphindex pairs
        self.charmaps = dict(
            [ (facename, self.fonts[facename].get_charmap())
                for facename in self.facenames])
        # a dict of glyphindex -> charcode pairs
        self.glyphmaps = {}
        for facename in self.facenames:
            charmap = self.charmaps[facename]
            self.glyphmaps[facename] = dict([(glyphind, charcode)
                for charcode, glyphind in charmap.items()])
        for fontface in self.fonts.values():
            fontface.clear()
        if self.output == 'SVG':
            # a list of "glyphs" we need to render this thing in SVG
            self.svg_glyphs=[]

    def set_canvas_size(self, w, h, pswriter=None):
        'Dimension the drawing canvas; may be a noop'
        # self.width = int(w)
        # self.height = int(h)
        # I don't know why this was different than the PS version
        self.width = w
        self.height = h
        if pswriter:
            self.pswriter = pswriter
        else:
            for fontface in self.fonts.values():
                fontface.set_bitmap_size(int(w), int(h))

    def render(self, ox, oy, facename, symbol, fontsize, dpi):
        filename = self.filenamesd[facename]
        uniindex, metrics, glyph, offset = self._get_info(facename,
                                                    symbol, fontsize, dpi)
        if self.output == 'SVG':
            oy += offset - 512/2048.*10.
            # TO-DO - make a method for it
            # This gets the name of the font.
            familyname = self.fonts[facename].get_sfnt()[(1,0,0,1)]
            thetext = unichr(uniindex)
            thetext.encode('utf-8')
            self.svg_glyphs.append((familyname, fontsize, thetext, ox, oy,
                                                            metrics))
        elif self.output == 'PS':
            # This should be changed to check for math mode or smth.
            #if filename == 'cmex10.ttf':
            #    oy += offset - 512/2048.*10.

            # Get the PS name of a glyph (his unicode integer code)
            # from the font object
            symbolname = self._get_glyph_name(uniindex, facename)
            psfontname = self.fonts[facename].postscript_name
            ps = """/%(psfontname)s findfont
%(fontsize)s scalefont
setfont
%(ox)f %(oy)f moveto
/%(symbolname)s glyphshow
""" % locals()
            self.pswriter.write(ps)
        else: # Agg
            fontface = self.fonts[facename]
            fontface.draw_glyph_to_bitmap(
            int(ox),  int(self.height - oy - metrics.ymax), glyph)

    def get_metrics(self, facename, symbol, fontsize, dpi):
        uniindex, metrics, glyph, offset  = \
                self._get_info(facename, symbol, fontsize, dpi)
        return metrics

    # Methods that must be overridden for fonts that are not unicode aware

    def _get_unicode_index(self, symbol):
        return get_unicode_index(symbol)

    def _get_glyph_name(self, uniindex, facename):
        """get_glyph_name(self, uniindex, facename) -> string

Returns the name of the glyph directly from the font object.

"""
        font = self.fonts[facename]
        glyphindex = self.glyphmaps[facename][uniindex]
        return font.get_glyph_name(glyphindex)

    def _get_info(self, facename, symbol, fontsize, dpi):
        'load the facename, metrics and glyph'
        #print hex(index), symbol, filename, facename
        key = facename, symbol, fontsize, dpi
        tup = self.glyphdict.get(key)
        if tup is not None:
            return tup
        filename = self.filenamesd[facename]
        fontface = self.fonts[facename]
        fontface.set_size(fontsize, dpi)
        head  = fontface.get_sfnt_table('head')
        uniindex = self._get_unicode_index(symbol)
        glyphindex = self.glyphmaps[facename][uniindex]
        glyph = fontface.load_char(uniindex)
        xmin, ymin, xmax, ymax = [val/64.0 for val in glyph.bbox]
        # This is black magic to me (Edin)
        if filename == 'cmex10.ttf':
            if self.output == 'PS':
                offset = -(head['yMin']+512)/head['unitsPerEm']*10.
            else:
                offset =  glyph.height/64.0/2 + 256.0/64.0*dpi/72.0
        else:
            offset = 0.
        metrics = Bunch(
            advance  = glyph.linearHoriAdvance/65536.0,
            height   = glyph.height/64.0,
            width    = glyph.width/64.0,
            xmin = xmin,
            xmax = xmax,
            ymin = ymin+offset,
            ymax = ymax+offset,
            )
        self.glyphdict[key] = uniindex, metrics, glyph, offset
        return self.glyphdict[key]


class MyUnicodeFonts(UnicodeFonts):
    _initialized = False
    def __init__(self):
        if not MyUnicodeFonts._initialized:
            prop = FontProperties()
            prop.set_family('serif')
            self.rmfile = fontManager.findfont(prop)

            prop.set_family('fantasy')
            self.calfile = fontManager.findfont(prop)

            prop.set_family('monospace')
            self.ttfile = fontManager.findfont(prop)

            prop.set_family('serif')
            prop.set_style('italic')
            self.itfile = fontManager.findfont(prop)
            self.filenamesd = { 'rm'  : self.rmfile,
                                'it'  : self.itfile,
                                'cal' : self.calfile,
                                'tt'  : self.ttfile,
                                }
            MyUnicodeFonts._initialized = True


# TO-DO: pretty much everything
class BakomaUnicodeFonts(UnicodeFonts):
    """A class that simulates Unicode support in the BaKoMa fonts"""

    filenamesd = { 'cal' : 'cmsy10.ttf',
                'rm'  : 'cmr10.ttf',
                'tt'  : 'cmtt10.ttf',
                'it'  : 'cmmi10.ttf',
                'bf'  : 'cmb10.ttf',
                'sf'  : 'cmss10.ttf',
                None  : 'cmmi10.ttf',
                }

    # We override the UnicodeFonts methods, that depend on Unicode support
    def _get_unicode_index(self, symbol):
        uniindex = get_unicode_index(symbol)

    # Should be deleted
    def _get_glyph_name(self, uniindex, facename):
        """get_glyph_name(self, uniindex, facename) -> string

Returns the name of the glyph directly from the font object.
Because BaKoma fonts don't support Unicode, 'uniindex' is misleading

"""
        font = self.fonts[facename]
        glyphindex = self.glyphmaps[facename][uniindex]
        return font.get_glyph_name(glyphindex)

    def _get_info(self, facename, symbol, fontsize, dpi):
        'load the facename, metrics and glyph'
        #print hex(index), symbol, filename, facename
        key = facename, symbol, fontsize, dpi
        tup = self.glyphdict.get(key)
        if tup is not None:
            return tup
        filename = self.filenamesd[facename]
        fontface = self.fonts[facename]
        fontface.set_size(fontsize, dpi)
        head  = fontface.get_sfnt_table('head')
        uniindex = self._get_unicode_index(symbol)
        glyphindex = self.glyphmaps[facename][uniindex]
        glyph = fontface.load_char(uniindex)
        xmin, ymin, xmax, ymax = [val/64.0 for val in glyph.bbox]
        # This is black magic to me (Edin)
        if filename == 'cmex10.ttf':
            if self.output == 'PS':
                offset = -(head['yMin']+512)/head['unitsPerEm']*10.
            else:
                offset =  glyph.height/64.0/2 + 256.0/64.0*dpi/72.0
        else:
            offset = 0.
        metrics = Bunch(
            advance  = glyph.linearHoriAdvance/65536.0,
            height   = glyph.height/64.0,
            width    = glyph.width/64.0,
            xmin = xmin,
            xmax = xmax,
            ymin = ymin+offset,
            ymax = ymax+offset,
            )
        self.glyphdict[key] = uniindex, metrics, glyph, offset
        return self.glyphdict[key]


# TO-DO: Implement all methods
class CMUUnicodeFonts(UnicodeFonts):
    """A class representing Computer Modern Unicode Fonts, made by
Andrey V. Panov
panov /at/ canopus. iacp. dvo. ru
They are distributed under the X11 License.

"""


# Old classes

class BakomaFonts(Fonts):
    """
    Use the Bakoma true type fonts for rendering
    """
    # allocate a new set of fonts
    basepath = os.path.join( get_data_path(), 'fonts', 'ttf' )

    fontmap = { 'cal' : 'Cmsy10',
                'rm'  : 'Cmr10',
                'tt'  : 'Cmtt10',
                'it'  : 'Cmmi10',
                'bf'  : 'Cmb10',
                'sf'  : 'Cmss10',
                None  : 'Cmmi10',
                'ex'  : 'Cmex10'
                }

    class CachedFont:
        def __init__(self, font):
            self.font     = font
            self.charmap  = font.get_charmap()
            self.glyphmap = dict(
                [(glyphind, ccode) for ccode, glyphind in self.charmap.items()])
    
    def __init__(self):
        self.glyphd          = {}
        self.fonts           = {}
        self.used_characters = {}

    def _get_font(self, font):
        """Looks up a CachedFont with its charmap and inverse charmap.
        font may be a TeX font name (cal, rm, it etc.), a Computer Modern
        font name (cmtt10, cmr10, etc.) or an FT2Font object."""
        if isinstance(font, str):
            if font not in self.fontmap.values():
                basename = self.fontmap[font]
            else:
                basename = font
        else:
            basename = font.postscript_name

        cached_font = self.fonts.get(basename)
        if cached_font is None:
            if isinstance(font, str):
                font = FT2Font(os.path.join(self.basepath, basename.lower() + ".ttf"))
                basename = font.postscript_name
            cached_font = self.CachedFont(font)
            self.fonts[basename] = cached_font
        return basename, cached_font

    def get_fonts(self):
        return [x.font for x in self.fonts.values()]
        
    def get_metrics(self, font, sym, fontsize, dpi):
        basename, font, metrics, symbol_name, num, glyph, offset = \
                self._get_info(font, sym, fontsize, dpi)
        return metrics

    def _get_offset(self, basename, cached_font, glyph, fontsize, dpi):
        if basename.lower() == 'cmex10':
            return glyph.height/64.0/2 + 256.0/64.0*dpi/72.0
        return 0.
    
    def _get_info (self, font, sym, fontsize, dpi):
        'load the cmfont, metrics and glyph with caching'
        if hasattr(font, 'postscript_name'):
            fontname = font.postscript_name
        else:
            fontname = font
            
        key = fontname, sym, fontsize, dpi
        tup = self.glyphd.get(key)

        if tup is not None: return tup
        
        if font in self.fontmap and latex_to_bakoma.has_key(sym):
            basename, num = latex_to_bakoma[sym]
            basename, cached_font = self._get_font(basename.capitalize())
            symbol_name = cached_font.font.get_glyph_name(num)
            num = cached_font.glyphmap[num]
        elif len(sym) == 1:
            basename, cached_font = self._get_font(font)
            num = ord(sym)
            symbol_name = cached_font.font.get_glyph_name(cached_font.charmap[num])
        else:
            num = 0
            raise ValueError('unrecognized symbol "%s"' % sym)

        font = cached_font.font
        font.set_size(fontsize, dpi)
        glyph = font.load_char(num)

        realpath, stat_key = get_realpath_and_stat(font.fname)
        used_characters = self.used_characters.setdefault(
            stat_key, (realpath, Set()))
        used_characters[1].update(unichr(num))
        
        xmin, ymin, xmax, ymax = [val/64.0 for val in glyph.bbox]
        offset = self._get_offset(basename, cached_font, glyph, fontsize, dpi)
        metrics = Bunch(
            advance  = glyph.linearHoriAdvance/65536.0,
            height   = glyph.height/64.0,
            width    = glyph.width/64.0,
            xmin = xmin,
            xmax = xmax,
            ymin = ymin+offset,
            ymax = ymax+offset,
            # iceberg is the amount of character that floats above the baseline
            # This is equivalent to TeX' "height"
            iceberg = glyph.horiBearingY/64.0
            )
        
        self.glyphd[key] = basename, font, metrics, symbol_name, num, glyph, offset
        return self.glyphd[key]

    def set_canvas_size(self, w, h):
        'Dimension the drawing canvas; may be a noop'
        self.width = int(w)
        self.height = int(h)
        for cached_font in self.fonts.values():
            cached_font.font.set_bitmap_size(int(w), int(h))

    def render(self, ox, oy, font, sym, fontsize, dpi):
        basename, font, metrics, symbol_name, num, glyph, offset = \
            self._get_info(font, sym, fontsize, dpi)

        font.draw_rect(0, 0, self.width - 1, self.height - 1)
        font.draw_glyph_to_bitmap(
            int(ox),  int(oy - metrics.ymax), glyph)

    def render_rect_filled(self, x1, y1, x2, y2):
        assert len(self.fonts)
        font = self.fonts.values()[0]
        print "filled rect:", x1, y1, x2, y2
        font.font.draw_rect_filled(x1, y1, x2, y2)
        
    def _old_get_kern(self, font, symleft, symright, fontsize, dpi):
        """
        Get the kerning distance for font between symleft and symright.

        font is one of tt, it, rm, cal or None

        sym is a single symbol(alphanum, punct) or a special symbol
        like \sigma.

        """
        basename = self.fontmap[font]
        cmfont = self.fonts[basename]
        cmfont.set_size(fontsize, dpi)
        kernd = cmkern[basename]
        key = symleft, symright
        kern = kernd.get(key,0)
        #print basename, symleft, symright, key, kern
        return kern

    def get_used_characters(self):
        return self.used_characters

    def get_xheight(self, font):
        basename, cached_font = self._get_font(font)
        pclt = cached_font.font.get_sfnt_table('pclt')
        return pclt['xHeight'] / 64.0 
    
class BakomaPSFonts(BakomaFonts):
    """
    Use the Bakoma postscript fonts for rendering to backend_ps
    """

    def _get_offset(self, basename, cached_font, glyph, fontsize, dpi):
        head = cached_font.font.get_sfnt_table("head")
        if basename.lower() == 'cmex10':
            return -(head['yMin']+512)/head['unitsPerEm']*10.
        return 0.
    
    def set_canvas_size(self, w, h, pswriter):
        'Dimension the drawing canvas; may be a noop'
        self.width  = w
        self.height = h
        self.pswriter = pswriter

    def render(self, ox, oy, font, sym, fontsize, dpi):
        basename, font, metrics, symbol_name, num, glyph, offset = \
                self._get_info(font, sym, fontsize, dpi)
        if basename.lower() == 'cmex10':
            oy += offset - 512/2048.*10.

        ps = """/%(basename)s findfont
%(fontsize)s scalefont
setfont
%(ox)f %(oy)f moveto
/%(symbol_name)s glyphshow
""" % locals()
        self.pswriter.write(ps)

class BakomaPDFFonts(BakomaPSFonts):
    """Hack of BakomaPSFonts for PDF support."""

    def render(self, ox, oy, font, sym, fontsize, dpi):
        basename, font, metrics, symbol_name, num, glyph, offset = \
                self._get_info(font, sym, fontsize, dpi)
        filename = font.fname
        if basename.lower() == 'cmex10':
            oy += offset - 512/2048.*10.

        self.pswriter.append((ox, oy, filename, fontsize, num))

class BakomaSVGFonts(BakomaFonts):
    """Hack of BakomaFonts for SVG support."""
    def __init__(self):
        BakomaFonts.__init__(self)
        self.svg_glyphs = []
    
    def render(self, ox, oy, font, sym, fontsize, dpi):
        basename, font, metrics, symbol_name, num, glyph, offset = \
                self._get_info(font, sym, fontsize, dpi)

        oy += offset - 512/2048.*10.
        thetext = unichr(num)
        thetext.encode('utf-8')
        self.svg_glyphs.append((font, fontsize, thetext, ox, oy, metrics))

class StandardPSFonts(Fonts):
    """
    Use the standard postscript fonts for rendering to backend_ps
    """
    fnames = ('psyr', 'pncri8a', 'pcrr8a', 'pncr8a', 'pzcmi8a')
    # allocate a new set of fonts
    basepath = os.path.join( get_data_path(), 'fonts', 'afm' )

    fontmap = { 'cal' : 'pzcmi8a',  # Zapf Chancery
                'rm'  : 'pncr8a',   # New Century Schoolbook
                'tt'  : 'pcrr8a',   # Courier  
                'it'  : 'pncri8a',  # New Century Schoolbook Italic
                'sf'  : 'phvr8a',   # Helvetica
                'bf'  : 'pncb8a',   # New Century Schoolbook Bold
                None  : 'psyr'      # Symbol
                }

    def __init__(self):
        self.glyphd = {}
        self.fonts = {}

    def _get_font(self, font):
        if isinstance(font, str):
            if font not in self.fontmap.values():
                basename = self.fontmap[font]
            else:
                basename = font
        else:
            basename = font.get_fontname()

        cached_font = self.fonts.get(basename)
        if cached_font is None:
            if isinstance(font, str):
                fname = os.path.join(self.basepath, basename + ".afm")
                cached_font = AFM(file(fname, 'r'))
                cached_font.fname = fname
                basename = cached_font.get_fontname()
            else:
                cached_font = font
            self.fonts[basename] = cached_font
        return basename, cached_font

    def get_fonts(self):
        return [x.font for x in self.fonts.values()]
        
    def _get_info (self, font, sym, fontsize, dpi):
        'load the cmfont, metrics and glyph with caching'
        if hasattr(font, 'get_fontname'):
            fontname = font.get_fontname()
        else:
            fontname = font

        key = fontname, sym, fontsize, dpi
        tup = self.glyphd.get(key)

        if tup is not None:
            return tup

        if sym in "0123456789()" and font == 'it':
            font = 'rm'

        if latex_to_standard.has_key(sym):
            font, num = latex_to_standard[sym]
            glyph = chr(num)
        elif len(sym) == 1:
            glyph = sym
            num = ord(glyph)
        else:
            raise ValueError('unrecognized symbol "%s"' % (sym))
        basename, font = self._get_font(font)    
        
        try:
            symbol_name = font.get_name_char(glyph)
        except KeyError:
            raise ValueError('unrecognized symbol "%s"' % (sym))

        offset = 0

        scale = 0.001 * fontsize

        xmin, ymin, xmax, ymax = [val * scale
                                  for val in font.get_bbox_char(glyph)]
        metrics = Bunch(
            advance  = (xmax-xmin),
            width    = font.get_width_char(glyph) * scale,
            height   = font.get_width_char(glyph) * scale,
            xmin = xmin,
            xmax = xmax,
            ymin = ymin+offset,
            ymax = ymax+offset
            )

        self.glyphd[key] = basename, font, metrics, symbol_name, num, glyph, offset
        return self.glyphd[key]

    def set_canvas_size(self, w, h, pswriter):
        'Dimension the drawing canvas; may be a noop'
        self.width  = w
        self.height = h
        self.pswriter = pswriter

    def render(self, ox, oy, font, sym, fontsize, dpi):
        basename, font, metrics, symbol_name, num, glyph, offset = \
                self._get_info(font, sym, fontsize, dpi)
        ps = """/%(basename)s findfont
%(fontsize)s scalefont
setfont
%(ox)f %(oy)f moveto
/%(symbol_name)s glyphshow
""" % locals()
        self.pswriter.write(ps)


    def get_metrics(self, font, sym, fontsize, dpi):
        basename, font, metrics, symbol_name, num, glyph, offset = \
                self._get_info(font, sym, fontsize, dpi)
        return metrics

    def get_kern(self, font, symleft, symright, fontsize, dpi):
        basename, font1, metrics, symbol_name, num, glyph1, offset = \
                self._get_info(font, symleft, fontsize, dpi)
        basename, font2, metrics, symbol_name, num, glyph2, offset = \
                self._get_info(font, symright, fontsize, dpi)
        if font1.get_fontname() == font2.get_fontname():
            basename, font = self._get_font(font)
            return font.get_kern_dist(glyph1, glyph2) * 0.001 * fontsize
        return 0

##############################################################################
# TeX-LIKE BOX MODEL

# The following is based directly on the document 'woven' from the
# TeX82 source code.  This information is also available in printed
# form:
#
#    Knuth, Donald E.. 1986.  Computers and Typesetting, Volume B:
#    TeX: The Program.  Addison-Wesley Professional.
#
# The most relevant "chapters" are:
#    Data structures for boxes and their friends
#    Shipping pages out (Ship class)
#    Packaging (hpack and vpack)
#    Data structures for math mode
#    Subroutines for math mode
#    Typesetting math formulas
#
# Many of the docstrings below refer to a numbered "node" in that
# book, e.g. §123
#
# Note that (as TeX) y increases downward, unlike many other parts of
# matplotlib.

class MathTextWarning(Warning):
    pass
    
class Node(object):
    """A node in a linked list.
    §133
    """
    def __init__(self):
        self.link = None
        
    def __repr__(self):
        s = self.__internal_repr__()
        if self.link:
            s += ' ' + self.link.__repr__()
        return s

    def __internal_repr__(self):
        return self.__class__.__name__

    def get_kerning(self, next):
        return 0.0
    
    def set_link(self, other):
        self.link = other
    
    def render(self, x, y):
        pass

class Box(Node):
    """Represents any node with a physical location.
    §135"""
    def __init__(self, width, height, depth):
        Node.__init__(self)
        self.width        = width
        self.height       = height
        self.depth        = depth
    
class CharNode(Box):
    """Represents a single character.  Unlike TeX, the font
    information and metrics are stored with each CharNode to make it
    easier to lookup the font metrics when needed.  Note that TeX
    boxes have a width, height, and depth, unlike Type1 and Truetype
    which use a full bounding box and an advance in the x-direction.
    The metrics must be converted to the TeX way, and the advance (if
    different from width) must be converted into a Kern node when the
    CharNode is added to its parent Hlist.
    §134"""
    def __init__(self, c, state):
        self.c = c
        self.font_manager = state.font_manager
        self.font = state.font
        self.fontsize = state.fontsize
        self.dpi = state.dpi
        metrics = self._metrics = self.font_manager.get_metrics(
            self.font, self.c, self.fontsize, self.dpi)
        Box.__init__(self, metrics.width, metrics.iceberg,
                     -(metrics.iceberg - metrics.height))
        
    def __internal_repr__(self):
        return self.c

    def get_kerning(self, next):
        """Return the amount of kerning between this and the given
        character.  Called when characters are strung together into
        Hlists to create Kern nodes."""
        # MGDTODO: Actually use kerning pairs
        return self._metrics.advance - self.width
    
    def render(self, x, y):
        """Render the character to the canvas"""
        self.font_manager.render(
            x, y,
            self.font, self.c, self.fontsize, self.dpi)
        
class List(Box):
    """A list of nodes (either horizontal or vertical).
    §135"""
    def __init__(self, elements):
        Box.__init__(self, 0., 0., 0.)
        self.shift_amount = 0.   # An arbitrary offset
        self.list_head    = None # The head of a linked list of Nodes in this box
        # The following parameters are set in the vpack and hpack functions
        self.glue_set     = 0.   # The glue setting of this list
        self.glue_sign    = 0    # 0: normal, -1: shrinking, 1: stretching
        self.glue_order   = 0    # The order of infinity (0 - 3) for the glue
        
        # Convert the Python list to a linked list
        if len(elements):
            elem = self.list_head = elements[0]
            for next in elements[1:]:
                elem.set_link(next)
                elem = next

    def __repr__(self):
        s = '[' + self.__internal_repr__()
        if self.list_head:
            s += ' ' + self.list_head.__repr__()
        s += ']'
        if self.link:
            s += ' ' + self.link.__repr__()
        return s

    def _determine_order(self, totals):
        """A helper function to determine the highest order of glue
        used by the members of this list.  Used by vpack and hpack."""
        o = 0
        for i in range(len(totals), 0, -1):
            if totals[i] != 0.0:
                o = i
                break
        return o
    
class Hlist(List):
    """A horizontal list of boxes.
    §135"""
    def __init__(self, elements, w=0., m='additional'):
        List.__init__(self, elements)
        self.do_kerning()
        self.hpack(w, m)

    def do_kerning(self):
        """Insert Kern nodes between CharNodes to set kerning.  The
        CharNodes themselves determine the amount of kerning they need
        (in get_kerning), and this function just creates the linked
        list in the correct way."""
        elem = self.list_head
        while elem is not None:
            next = elem.link
            kerning_distance = elem.get_kerning(next)
            if kerning_distance != 0.:
                kern = Kern(kerning_distance)
                elem.link = kern
                kern.link = next
            elem = next
        
    def hpack(self, w=0., m='additional'):
        """The main duty of hpack is to compute the dimensions of the
        resulting boxes, and to adjust the glue if one of those dimensions is
        pre-specified. The computed sizes normally enclose all of the material
        inside the new box; but some items may stick out if negative glue is
        used, if the box is overfull, or if a \vbox includes other boxes that
        have been shifted left.

        w: specifies a width
        m: is either 'exactly' or 'additional'.

        Thus, hpack(w, exactly) produces a box whose width is exactly w, while
        hpack (w, additional ) yields a box whose width is the natural width
        plus w.  The default values produce a box with the natural width.
        §644, §649"""
        self.shift_amount = 0.
        h = 0.
        d = 0.
        x = 0.
        total_stretch = [0.] * 4
        total_shrink = [0.] * 4
        p = self.list_head
        while p is not None:
            # Layout characters in a tight inner loop (common case)
            while isinstance(p, CharNode):
                x += p.width
                h = max(h, p.height)
                d = max(d, p.depth)
                p = p.link
            if p is None:
                break
            
            if isinstance(p, (List, Rule, Unset)):
                x += p.width
                if hasattr(p, 'shift_amount'):
                    s = p.shift_amount
                else:
                    s = 0.
                if p.height is not None and p.depth is not None:
                    h = max(h, p.height - s)
                    d = max(d, p.depth + s)
            elif isinstance(p, Glue):
                glue_spec = p.glue_spec
                x += glue_spec.width
                total_stretch[glue_spec.stretch_order] += glue_spec.stretch
                total_shrink[glue_spec.shrink_order] += glue_spec.shrink
            elif isinstance(p, Kern):
                x += p.width
            p = p.link
        self.height = h
        self.depth = d

        if m == 'additional':
            w += x
        self.width = w
        x = w - x
        
        if x == 0.:
            self.glue_sign = 0
            self.glue_order = 0
            self.glue_ratio = 0.
            return
        if x > 0.:
            o = self._determine_order(total_stretch)
            self.glue_order = o
            self.glue_sign = 1
            if total_stretch[o] != 0.:
                self.glue_set = x / total_stretch[o]
            else:
                self.glue_sign = 0
                self.glue_ratio = 0.
            if o == 0:
                if self.list_head is not None:
                    warn("Overfull hbox: %r" % self, MathTextWarning)
        else:
            o = self._determine_order(total_shrink)
            self.glue_order = o
            self.glue_sign = -1
            if total_shrink[o] != 0.:
                self.glue_set = x / total_shrink[o]
            else:
                self.glue_sign = 0
                self.glue_ratio = 0.
            if o == 0:
                if self.list_head is not None:
                    warn("Underfull vbox: %r" % self, MathTextWarning)

class Vlist(List):
    """A vertical list of boxes.
    §137"""
    def __init__(self, elements, h=0., m='additional'):
        List.__init__(self, elements)
        self.vpack(h, m)

    def vpack(self, h=0., m='additional', l=float('inf')):
        """The main duty of vpack is to compute the dimensions of the
        resulting boxes, and to adjust the glue if one of those dimensions is
        pre-specified.

        h: specifies a height
        m: is either 'exactly' or 'additional'.
        l: a maximum height

        Thus, vpack(h, exactly) produces a box whose width is exactly w, while
        hpack (w, additional ) yields a box whose width is the natural width
        plus w.  The default values produce a box with the natural width.
        §644, §668"""
        self.shift_amount = 0.
        w = 0.
        d = 0.
        x = 0.
        total_stretch = [0.] * 4
        total_shrink = [0.] * 4
        p = self.list_head
        while p is not None:
            if isinstance(p, CharNode):
                raise RuntimeError("Internal error in mathtext")
            elif isinstance(p, (List, Rule, Unset)):
                x += d + p.height
                d = p.depth
                if hasattr(p, 'shift_amount'):
                    s = p.shift_amount
                else:
                    s = 0.
                if p.width is not None:
                    w = max(w, p.width + s)
            elif isinstance(p, Glue):
                x += d
                d = 0.
                glue_spec = p.glue_spec
                x += glue_spec.width
                total_stretch[glue_spec.stretch_order] += glue_spec.stretch
                total_shrink[glue_spec.shrink_order] += glue_spec.shrink
            elif isinstance(p, Kern):
                x += d + p.width
                d = 0.
            p = p.link

        self.width = w
        if d > l:
            x += d - l
            self.depth = l
        else:
            self.depth = d

        if m == 'additional':
            h += x
        self.height = h
        x = h - x

        if x == 0:
            self.glue_sign = 0
            self.glue_order = 0
            self.glue_ratio = 0.
            return
        if x > 0.:
            o = self._determine_order(total_stretch)
            self.glue_order = o
            self.glue_sign = 1
            if total_stretch[o] != 0.:
                self.glue_set = x / total_stretch[o]
            else:
                self.glue_sign = 0
                self.glue_ratio = 0.
            if o == 0:
                if self.list_head is not None:
                    warn("Overfull vbox: %r" % self, MathTextWarning)
        else:
            o = self._determine_order(total_shrink)
            self.glue_order = o
            self.glue_sign = -1
            if total_shrink[o] != 0.:
                self.glue_set = x / total_shrink[o]
            else:
                self.glue_sign = 0
                self.glue_ratio = 0.
            if o == 0:
                if self.list_head is not None:
                    warn("Underfull vbox: %r" % self, MathTextWarning)
                    
class Rule(Box):
    """A Rule node stands for a solid black rectangle; it has width,
    depth, and height fields just as in an Hlist. However, if any of these
    dimensions is None, the actual value will be determined by running the
    rule up to the boundary of the innermost enclosing box. This is called
    a “running dimension.” The width is never running in an Hlist; the
    height and depth are never running in a Vlist.
    §138"""
    def __init__(self, width, height, depth, state):
        Box.__init__(self, width, height, depth)
        self.font_manager = state.font_manager
    
    def render(self, x, y, w, h):
        self.font_manager.render_rect_filled(x, y, x + w, y + h)
    
class Hrule(Rule):
    """Convenience class to create a horizontal rule."""
    def __init__(self, state):
        # MGDTODO: Get the line width from the font information
        Rule.__init__(self, None, 0.5, 0.5, state)

class Vrule(Rule):
    """Convenience class to create a vertical rule."""
    def __init__(self, state):
        # MGDTODO: Get the line width from the font information
        Rule.__init__(self, 1.0, None, None, state)
        
class Glue(Node):
    """Most of the information in this object is stored in the underlying
    GlueSpec class, which is shared between multiple glue objects.  (This
    is a memory optimization which probably doesn't matter anymore, but it's
    easier to stick to what TeX does.)
    §149, §152"""
    def __init__(self, glue_type, copy=False):
        Node.__init__(self)
        self.glue_subtype   = 'normal'
        if is_string_like(glue_type):
            glue_spec = GlueSpec.factory(glue_type)
        elif isinstance(glue_type, GlueSpec):
            glue_spec = glue_type
        else:
            raise ArgumentError("glue_type must be a glue spec name or instance.")
        if copy:
            glue_spec = glue_spec.copy()
        self.glue_spec      = glue_spec

class GlueSpec(object):
    """§150, §151"""
    def __init__(self, width=0., stretch=0., stretch_order=0, shrink=0., shrink_order=0):
        self.width         = width
        self.stretch       = stretch
        self.stretch_order = stretch_order
        self.shrink        = shrink
        self.shrink_order  = shrink_order

    def copy(self):
        return GlueSpec(
            self.width,
            self.stretch,
            self.stretch_order,
            self.shrink,
            self.shrink_order)
        
    def factory(glue_type):
        return self._types[glue_type]
    factory = staticmethod(factory)

GlueSpec._types = {
    'lineskip': GlueSpec(0, 0, 0, 0, 0)
}
    
class Kern(Node):
    """A Kern node has a width field to specify a (normally negative)
    amount of spacing. This spacing correction appears in horizontal lists
    between letters like A and V when the font designer said that it looks
    better to move them closer together or further apart. A kern node can
    also appear in a vertical list, when its ‘width ’ denotes additional
    spacing in the vertical direction.
    §155"""
    def __init__(self, width, subtype='normal'):
        Node.__init__(self)
        self.width = width
        self.subtype = subtype

class Unset(Node):
    pass
        
# MGDTODO: Move this to cbook    
def clamp(value, min, max):
    if value < min:
        return min
    if value > max:
        return max
    return value
        
class Ship(object):
    """Since boxes can be inside of boxes inside of boxes, the main
    work of Ship is done by two mutually recursive routines, hlist_out
    and vlist_out , which traverse the Hlists and Vlists inside of
    horizontal and vertical boxes.  The global variables used in TeX to
    store state as it processes have become member variables here.
    §592."""
    def __call__(self, ox, oy, box):
        self.max_push    = 0 # Deepest nesting of push commands so far
        self.cur_s       = 0
        self.cur_v       = 0.
        self.cur_h       = 0.
        print box
        self.off_h       = ox
        self.off_v       = oy + box.height
        self.hlist_out(box)
        
    def hlist_out(self, box):
        cur_g         = 0
        cur_glue      = 0.
        glue_order    = box.glue_order
        glue_sign     = box.glue_sign
        p             = box.list_head
        base_line     = self.cur_v
        left_edge     = self.cur_h
        self.cur_s    += 1
        self.max_push = max(self.cur_s, self.max_push)

        while p:
            while isinstance(p, CharNode):
                p.render(self.cur_h + self.off_h, self.cur_v + self.off_v)
                self.cur_h += p.width
                p = p.link
            if p is None:
                break
                
            if isinstance(p, List):
                # §623
                if p.list_head is None:
                    self.cur_h += p.width
                else:
                    edge = self.cur_h
                    self.cur_v = base_line + p.shift_amount
                    if isinstance(p, Hlist):
                        self.hlist_out(p)
                    else:
                        self.vlist_out(p)
                    self.cur_h = edge + p.width
                    self.cur_v = base_line
            elif isinstance(p, Rule):
                # §624
                rule_height = p.height
                rule_depth  = p.depth
                rule_width  = p.width
                if rule_height is None:
                    rule_height = box.height
                if rule_depth is None:
                    rule_depth = box.depth
                if rule_height > 0 and rule_width > 0:
                    self.cur_v = baseline + rule_depth
                    p.render(self.cur_h + self.off_h,
                             self.cur_v + self.off_v,
                             rule_width, rule_height)
                    self.cur_v = baseline
                self.cur_h += rule_width
            elif isinstance(p, Glue):
                # §625
                glue_spec = p.glue_spec
                rule_width = glue_spec.width - cur_g
                if g_sign != 0: # normal
                    if g_sign == 1: # stretching
                        if glue_spec.stretch_order == glue_order:
                            cur_glue += glue_spec.stretch
                            glue_temp = clamp(float(box.glue_set) * cur_glue,
                                             1000000000., -10000000000.)
                            cur_g = round(glue_temp)
                    elif glue_spec.shrink_order == glue_order:
                        cur_glue += glue_spec.shrink
                        glue_temp = clamp(float(box.glue_set) * cur_glue,
                                         1000000000., -10000000000.)
                        cur_g = round(glue_temp)
                rule_width += cur_g
                self.cur_h += rule_width
            elif isinstance(p, Kern):
                self.cur_h += p.width
            p = p.link
        self.cur_s -= 1

    def vlist_out(self, box):
        cur_g         = 0
        cur_glue      = 0.
        glue_order    = box.glue_order
        glue_sign     = box.glue_sign
        p             = box.list_head
        self.cur_s    += 1
        self.max_push = max(self.max_push, self.cur_s)
        left_edge     = self.cur_h
        self.cur_v    -= box.height
        top_edge      = self.cur_v

        while p:
            if isinstance(p, CharNode):
                raise RuntimeError("Internal error in mathtext")
            elif isinstance(p, List):
                if p.list_head is None:
                    self.cur_v += p.height + p.depth
                else:
                    self.cur_v += p.height
                    self.cur_h = left_edge + p.shift_amount
                    save_v = self.cur_v
                    if isinstance(p, Hlist):
                        self.hlist_out(p)
                    else:
                        self.vlist_out(p)
                    self.cur_v = save_v + p.depth
                    self.cur_h = left_edge
            elif isinstance(p, Rule):
                rule_height = p.height
                rule_depth = p.depth
                rule_width = p.width
                if rule_width is None:
                    rule_width = box.width
                rule_height += rule_depth
                if rule_height > 0 and rule_depth > 0:
                    self.cur_v += rule_height
                    p.render(self.cur_h + self.off_h,
                             self.cur_v + self.off_v,
                             rule_width, rule_height)
            elif isinstance(p, Glue):
                glue_spec = p.glue_spec
                rule_height = glue_spec.width - cur_g
                if g_sign != 0: # normal
                    if g_sign == 1: # stretching
                        if glue_spec.stretch_order == glue_order:
                            cur_glue += glue_spec.stretch
                            glue_temp = clamp(float(box.glue_set) * cur_glue,
                                             1000000000., -10000000000.)
                            cur_g = round(glue_temp)
                    elif glue_spec.shrink_order == glue_order: # shrinking
                        cur_glue += glue_spec.shrink
                        glue_temp = clamp(float(box.glue_set) * cur_glue,
                                         1000000000., -10000000000.)
                        cur_g = round(glue_temp)
                rule_height += cur_g
                self.cur_v += rule_height
            elif isinstance(p, Kern):
                self.cur_v += p.width
                            
            p = p.link
        self.cur_s -= 1
        
ship = Ship()

# TODO: Ligature nodes? (143)

# TODO: Unset box?

##############################################################################
# NOADS

class Noad:
    def __init__(self, nucleus=None, subscr=None, superscr=None):
        self.link = None
        self.nucleus = nucleus
        self.subscr = subscr
        self.superscr = superscr

class OrdNoad(Noad):
    pass

class OpNoad(Noad):
    pass

class BinNoad(Noad):
    pass

class RelNoad(Noad):
    pass

class OpenNoad(Noad):
    pass

class CloseNoad(Noad):
    pass

class PunctNoad(Noad):
    pass

class InnerNoad(Noad):
    pass

class RadicalNoad(Noad):
    def __init__(self, nucleus=None, subscr=None, superscr=None, left_delim_font=None, left_delim_char=None):
        Noad.__init__(self, nucleus, subscr, superscr)
        self.left_delim = left_delim

class NoadField:
    def __init__(self):
        pass

class MathChar(NoadField):
    def __init__(self, char, font):
        self.char = char
        self.font = font

class SubMlist(NoadField):
    def __init__(self):
        pass

##############################################################################
# PARSER
    
class Parser:
    class State:
        def __init__(self, font_manager, font, fontsize, dpi):
            self.font_manager = font_manager
            self.font = font
            self.fontsize = fontsize
            self.dpi = dpi

        def copy(self):
            return Parser.State(
                self.font_manager,
                self.font,
                self.fontsize,
                self.dpi)
            
    def __init__(self):
        # All forward declarations are here
        font = Forward().setParseAction(self.font).setName("font")
        latexfont = Forward().setParseAction(self.latexfont).setName("latexfont")
        subsuper = Forward().setParseAction(self.subsuperscript).setName("subsuper")
        overunder = Forward().setParseAction(self.overunder).setName("overunder")
        placeable = Forward().setName("placeable")
        simple = Forward().setName("simple")
        self._expression = Forward().setParseAction(self.finish).setName("finish")

        lbrace       = Literal('{').suppress().setParseAction(self.start_group).setName("start_group")
        rbrace       = Literal('}').suppress().setParseAction(self.end_group).setName("end_group")
        lbrack       = Literal('[')
        rbrack       = Literal(']')
        lparen       = Literal('(')
        rparen       = Literal(')')
        grouping     =(lbrack 
                     | rbrack 
                     | lparen 
                     | rparen)

        bslash       = Literal('\\')

        langle       = Literal('<')
        rangle       = Literal('>')
        equals       = Literal('=')
        relation     =(langle
                     | rangle
                     | equals)

        colon        = Literal(':')
        comma        = Literal(',')
        period       = Literal('.')
        semicolon    = Literal(';')
        exclamation  = Literal('!')
        punctuation  =(colon
                     | comma
                     | period
                     | semicolon)

        at           = Literal('@')
        percent      = Literal('%')
        ampersand    = Literal('&')
        misc         =(exclamation
                     | at
                     | percent
                     | ampersand)

        accent       = oneOf("hat check dot breve acute ddot grave tilde bar vec "
                             "\" ` ' ~ . ^")

        function     = oneOf("arccos csc ker min arcsin deg lg Pr arctan det lim sec "
                             "arg dim liminf sin cos exp limsup sinh cosh gcd ln sup "
                             "cot hom log tan coth inf max tanh")

        number       = Combine(Word(nums) + Optional(Literal('.')) + Optional( Word(nums) ))

        plus         = Literal('+')
        minus        = Literal('-')
        times        = Literal('*')
        div          = Literal('/')
        binop        =(plus 
                     | minus
                     | times
                     | div)

        fontname     = oneOf("rm cal it tt sf bf")
        latex2efont  = oneOf("mathrm mathcal mathit mathtt mathsf mathbf")

        texsym       = Combine(bslash + Word(alphanums) + NotAny("{"))

        char         = Word(alphanums + ' ', exact=1).leaveWhitespace()

        space        =(FollowedBy(bslash)
                     +   (Literal(r'\ ')
                       |  Literal(r'\/')
                       |  Group(Literal(r'\hspace{') + number + Literal('}'))
                         )
                      ).setParseAction(self.space).setName('space')

        symbol       = Regex("(" + ")|(".join(
                       [
                         r"\\[a-zA-Z0-9]+(?!{)",
                         r"[a-zA-Z0-9 ]",
                         r"[+\-*/]",
                         r"[<>=]",
                         r"[:,.;!]",
                         r"[!@%&]",
                         r"[[\]()]",
                         r"\\\$"
                       ])
                     + ")"
                     ).setParseAction(self.symbol).leaveWhitespace()

        _symbol      =(texsym
                     | char
                     | binop
                     | relation
                     | punctuation
                     | misc
                     | grouping
                     ).setParseAction(self.symbol).leaveWhitespace()

        accent       = Group(
                         Combine(bslash + accent)
                       + Optional(lbrace)
                       + symbol
                       + Optional(rbrace)
                     ).setParseAction(self.accent).setName("accent")

        function     =(Suppress(bslash)
                     + function).setParseAction(self.function).setName("function")

        group        = Group(
                         lbrace
                       + OneOrMore(
                           simple
                         )
                       + rbrace
                     ).setParseAction(self.group).setName("group")

        font        <<(Suppress(bslash)
                     + fontname)

        latexfont   << Group(
                         Suppress(bslash)
                       + latex2efont
                       + group)

        frac         = Group(
                       Suppress(
                         bslash
                       + Literal("frac")
                       )
                     + group
                     + group
                     ).setParseAction(self.frac).setName("frac")

        placeable   <<(accent
                     ^ function  
                     ^ symbol
                     ^ group
                     ^ frac
                     )

        simple      <<(space
                     | font
                     | latexfont
                     | overunder)

        subsuperop   =(Literal("_")
                     | Literal("^")
                     )   

        subsuper    << Group(
                         (
                           placeable
                         + ZeroOrMore(
                             subsuperop
                           + subsuper
                           )
                         )
                       | (subsuperop + placeable)
                     )

        overunderop  =(
                        ( Suppress(bslash)
                        + Literal(r"over")
                        )
                     |  ( Suppress(bslash)
                        + Literal(r"under")
                        )
                     )   

        overunder   << Group(
                         (
                           subsuper
                         + ZeroOrMore(
                             overunderop
                           + overunder
                           )
                         )
                     )

        math         = OneOrMore(
                       simple
                     ).setParseAction(self.math).setName("math")

        math_delim   =(~bslash
                     + Literal('$'))

        non_math     = Regex(r"(?:[^$]|(?:\\\$))*"
                     ).setParseAction(self.non_math).setName("non_math").leaveWhitespace()

        self._expression  <<(
                         non_math
                       + ZeroOrMore(
                           Suppress(math_delim)
                         + math
                         + Suppress(math_delim)
                         + non_math
                         )
                       )

    def parse(self, s, fonts_object, default_font, fontsize, dpi):
        self._state_stack = [self.State(fonts_object, default_font, fontsize, dpi)]
        self._expression.parseString(s)
        return self._expr
        
    def get_state(self):
        return self._state_stack[-1]

    def pop_state(self):
        self._state_stack.pop()

    def push_state(self):
        self._state_stack.append(self.get_state().copy())
        
    def finish(self, s, loc, toks):
        self._expr = Hlist(toks)
        return [self._expr]
        
    def math(self, s, loc, toks):
        hlist = Hlist(toks)
        self.pop_state()
        return [hlist]

    def non_math(self, s, loc, toks):
        #~ print "non_math", toks
        # This is a hack, but it allows the system to use the
        # proper amount of advance when going from non-math to math
        s = toks[0] + ' '
        symbols = [CharNode(c, self.get_state()) for c in s]
        hlist = Hlist(symbols)
        self.push_state()
        self.get_state().font = 'it'
        return [hlist]
    
    def space(self, s, loc, toks):
        assert(len(toks)==1)

        if toks[0]==r'\ ': num = 0.30 # 30% of fontsize
        elif toks[0]==r'\/': num = 0.1 # 10% of fontsize
        else:  # vspace
            num = float(toks[0][1]) # get the num out of \hspace{num}

        element = SpaceElement(num)
        self.symbols.append(element)
        return [element]

#     def symbol(self, s, loc, toks):
#         assert(len(toks)==1)
#         #print "symbol", toks
        
#         s  = toks[0]
#         if charOverChars.has_key(s):
#             under, over, pad = charOverChars[s]
#             font, tok, scale = under
#             sym = SymbolElement(tok)
#             if font is not None:
#                 sym.set_font(font, hardcoded=True)
#             sym.set_scale(scale)
#             sym.set_pady(pad)

#             font, tok, scale = over
#             sym2 = SymbolElement(tok)
#             if font is not None:
#                 sym2.set_font(font, hardcoded=True)
#             sym2.set_scale(scale)

#             sym.neighbors['above'] = sym2
#             self.symbols.append(sym2)
#         else:
#             sym = SymbolElement(toks[0], self.current_font)
#         self.symbols.append(sym)

#         return [sym]

    def symbol(self, s, loc, toks):
        return [CharNode(toks[0], self.get_state())]

    space = symbol
    
    def accent(self, s, loc, toks):
        assert(len(toks)==1)
        accent, sym = toks[0]

        d = {
            r'\hat'   : r'\circumflexaccent',
            r'\breve' : r'\combiningbreve',
            r'\bar'   : r'\combiningoverline',
            r'\grave' : r'\combininggraveaccent',
            r'\acute' : r'\combiningacuteaccent',
            r'\ddot'  : r'\combiningdiaeresis',
            r'\tilde' : r'\combiningtilde',
            r'\dot'   : r'\combiningdotabove',
            r'\vec'   : r'\combiningrightarrowabove',
            r'\"'     : r'\combiningdiaeresis',
            r"\`"     : r'\combininggraveaccent',
            r"\'"     : r'\combiningacuteaccent',
            r'\~'     : r'\combiningtilde',
            r'\.'     : r'\combiningdotabove',
            r'\^'   : r'\circumflexaccent',
             }
        above = AccentElement(d[accent])
        sym.neighbors['above'] = above
        sym.set_pady(1)
        self.symbols.append(above)
        return [sym]

    def function(self, s, loc, toks):
        #~ print "function", toks
        symbols = [FontElement("rm")]
        for c in toks[0]:
            sym = SymbolElement(c)
            symbols.append(sym)
            self.symbols.append(sym)
        return [GroupElement(symbols)]

    def start_group(self, s, loc, toks):
        self.push_state()
    
    def group(self, s, loc, toks):
        grp = Hlist(toks[0])
        return [grp]

    def end_group(self, s, loc, toks):
        self.pop_state()
        
    def font(self, s, loc, toks):
        assert(len(toks)==1)
        name = toks[0]
        self.get_state().font = name
        return []

    def latexfont(self, s, loc, toks):
        assert(len(toks)==1)
        name, grp = toks[0]
        if len(grp.elements):
            font = FontElement(name[4:])
            font.neighbors['right'] = grp.elements[0]
            grp.elements.insert(0, font)
            return [grp]
        return []
    
    _subsuperscript_names = {
        'normal':    ['subscript', 'superscript'],
        'overUnder': ['below', 'above']
    }

    _subsuperscript_indices = {
        '_'      : ('normal', (0, 1)),
        '^'      : ('normal', (1, 0)),
        'over'   : ('overUnder', (0, 1)),
        'under'  : ('overUnder', (1, 0))
    }
         
    def subsuperscript(self, s, loc, toks):
        assert(len(toks)==1)
        #~ print 'subsuperscript', toks

        if len(toks[0]) == 1:
            return toks[0].asList()
        if len(toks[0]) == 3:
            prev, op, next = toks[0]
        elif len(toks[0]) == 2:
            prev = SpaceElement(0)
            op, next = toks[0]
        else:
            raise ParseException("Unable to parse subscript/superscript construct.")

        relation_type, (index, other_index) = self._subsuperscript_indices[op]
        if self.is_overunder(prev):
            relation_type = 'overUnder'
        names = self._subsuperscript_names[relation_type]

        prev.neighbors[names[index]] = next

        for compound in self._subsuperscript_names.values():
            if compound[other_index] in next.neighbors:
                prev.neighbors[names[other_index]] = \
                    next.neighbors[compound[other_index]]
                del next.neighbors[compound[other_index]]
            elif compound[index] in next.neighbors:
                raise ValueError(
                    "Double %ss" %
                    self._subsuperscript_names['normal'][index])
        return [prev]

    def is_overunder(self, prev):
        return isinstance(prev, SymbolElement) and overunder_symbols.has_key(prev.sym)

    def frac(self, s, loc, toks):
        assert(len(toks)==1)
        assert(len(toks[0])==2)
        #~ print 'subsuperscript', toks
        
        top, bottom = toks[0]
        vlist = Vlist([bottom, Hrule(self.get_state()), top])
        # vlist.shift_amount = 8
        return [vlist]

    overunder = subsuperscript
    

####

##############################################################################
# MAIN

class math_parse_s_ft2font_common:
    """
    Parse the math expression s, return the (bbox, fonts) tuple needed
    to render it.

    fontsize must be in points

    return is width, height, fonts
    """
    major, minor1, minor2, tmp, tmp = sys.version_info
    if major==2 and minor1==2:
        raise SystemExit('mathtext broken on python2.2.  We hope to get this fixed soon')

    parser = None
    
    def __init__(self, output):
        self.output = output
        self.cache = {}

    def __call__(self, s, dpi, prop, angle=0):
        cacheKey = (s, dpi, hash(prop), angle)
        if self.cache.has_key(cacheKey):
            w, h, fontlike, used_characters = self.cache[cacheKey]
            return w, h, fontlike, used_characters

        use_afm = False
        if self.output == 'SVG':
            font_manager = BakomaSVGFonts()
        elif self.output == 'Agg':
            font_manager = BakomaFonts()
        elif self.output == 'PS':
            if rcParams['ps.useafm']:
                font_manager = StandardPSFonts()
                use_afm = True
            else:
                font_manager = BakomaPSFonts()
        elif self.output == 'PDF':
            font_manager = BakomaPDFFonts()
        
        fontsize = prop.get_size_in_points()
            
        if use_afm:
            fname = fontManager.findfont(prop, fontext='afm')
            default_font = AFM(file(fname, 'r'))
            default_font.fname = fname
        else:
            fname = fontManager.findfont(prop)
            default_font = FT2Font(fname)

        if self.parser is None:
            self.__class__.parser = Parser()
        box = self.parser.parse(s, font_manager, default_font, fontsize, dpi)
        w, h = box.width, box.height + box.depth
        w += 4
        h += 4
        font_manager.set_canvas_size(w,h)
        
        ship(2, 2, box)
        
        if self.output == 'SVG':
            # The empty list at the end is for lines
            svg_elements = Bunch(svg_glyphs=self.font_manager.svg_glyphs,
                    svg_lines=[])
            self.cache[cacheKey] = \
                w, h, svg_elements, font_manager.get_used_characters()
        elif self.output == 'Agg':
            self.cache[cacheKey] = \
                w, h, font_manager.get_fonts(), font_manager.get_used_characters()
        elif self.output in ('PS', 'PDF'):
            self.cache[cacheKey] = \
                w, h, pswriter, font_manager.get_used_characters()
        return self.cache[cacheKey]
            
if rcParams["mathtext.mathtext2"]:
    from matplotlib.mathtext2 import math_parse_s_ft2font
    from matplotlib.mathtext2 import math_parse_s_ft2font_svg
else:
    math_parse_s_ft2font = math_parse_s_ft2font_common('Agg')
    math_parse_s_ft2font_svg = math_parse_s_ft2font_common('SVG')
math_parse_s_ps = math_parse_s_ft2font_common('PS')
math_parse_s_pdf = math_parse_s_ft2font_common('PDF')

if 0: #__name__=='___main__':

    stests = [
            r'$dz/dt \/ = \/ \gamma x^2 \/ + \/ \rm{sin}(2\pi y+\phi)$',
            r'$dz/dt \/ = \/ \gamma xy^2 \/ + \/ \rm{s}(2\pi y+\phi)$',
            r'$x^1 2$',
            r'$\alpha_{i+1}^j \/ = \/ \rm{sin}(2\pi f_j t_i) e^{-5 t_i/\tau}$',
            r'$\cal{R}\prod_{i=\alpha_{i+1}}^\infty a_i\rm{sin}(2 \pi f x_i)$',
            r'$\bigodot \bigoplus \cal{R} a_i\rm{sin}(2 \pi f x_i)$',
            r'$x_i$',
            r'$5\/\angstrom\hspace{ 2.0 }\pi$',
            r'$x+1$',
            r'$i$',
            r'$i^j$',
            ]
    #~ w, h, fonts = math_parse_s_ft2font(s, 20, 72)
    for s in stests:
        try:
            print s
            print (expression + StringEnd()).parseString( s[1:-1] )
        except ParseException, pe:
            print "*** ERROR ***", pe.msg
            print s
            print 'X' + (' '*pe.loc)+'^'
            # how far did we get?
            print expression.parseString( s[1:-1] )
        print

    #w, h, fonts = math_parse_s_ps(s, 20, 72)

# MGDTODO: Below here is out-of-date
if __name__=='__main__':
    Element.fonts = DummyFonts()
    for i in range(5,20):
        s = '$10^{%02d}$'%i
        print 'parsing', s
        w, h, fonts = math_parse_s_ft2font(s, dpi=27, fontsize=12, angle=0)
    if 0:
        Element.fonts = DummyFonts()
        handler.clear()
        expression.parseString( s )

        handler.expr.set_size_info(12, 72)

        # set the origin once to allow w, h compution
        handler.expr.set_origin(0, 0)
        for e in handler.symbols:
            assert(hasattr(e, 'metrics'))
