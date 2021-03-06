from _sdl.structs import SDLError

from gsdl2.color import convert_to_color
from gsdl2.pkgdata import getResource
from gsdl2.sysfont import get_fonts, match_font, SysFont

__all__ = ['Font', 'SysFont']

import logging
import os

import sdl
from gsdl2.sdlconstants import (
    TTF_STYLE_NORMAL,
    TTF_STYLE_BOLD,
    TTF_STYLE_ITALIC,
    TTF_STYLE_UNDERLINE,
    TTF_STYLE_STRIKETHROUGH,
    TTF_HINTING_NORMAL,
    TTF_HINTING_LIGHT,
    TTF_HINTING_MONO,
    TTF_HINTING_NONE,
)
from gsdl2.locals import utf8

log = logging.getLogger(__name__)


# init ttf library
def init():
    sdl.ttf.init()

# Default font
_font_defaultname = "freesansbold.ttf"

class Font(object):
    def __init__(self, filename, pointsize=12):
        self.__filename = filename
        self.__pointsize = pointsize
        if not filename or filename == _font_defaultname:
            filename = getResource(_font_defaultname).name
            # Scaling as from pygame/src/font.c
            pointsize = int(pointsize * 0.6875)
            if pointsize < 1:
                pointsize = 1
        else:
            try:
                assert os.access(filename, os.F_OK)
            except AssertionError:
                raise AssertionError('cannot read font file: {}'.format(filename))

        self.__sdl_font = sdl.ttf.openFont(utf8(filename), pointsize)
        if self.__sdl_font == sdl.ffi.NULL:
            log.critical(sdl.ffi.string(sdl.getError()).decode('utf-8'))
            raise SDLError()

    # render is incompatible with pygame because
    # render has no argument - "antialiasing" as it used by default
    # this is ugly hack to make both versions work! (from pygame and gsdl2)
    def render(self, *args, **kwargs):
        """render text, returning a Surface

        If palette is True: the TTF_RenderSolid* routines are used.
        If wrap_length > 0: the TTF_RenderBlendedWrapped* routines are used.
        If background is not None: the TTF_RenderShaded* routined are used.
        Else: the TTF_RenderBlended* routines (not wrapped) are used.

        :param text: string; the text to render
        :param color: color.Color; foreground color
        :param background: color.Color; (optional) background colod
        :param encoding: one of: 'utf-8', 'ascii', 'unicode', 'glyph'
        :param wrap_length: pixel width to wrap text; 0 (zero) means no wrapping
        :param palette: use 8-bit palette rendering
        :return:
        """
        # if second argument is int - it's antialias value, we just ignore it:)
        if isinstance(args[1], int):
            return self._render(args[0], *args[2:], **kwargs)
        # if everything normal - call standart func
        else:
            return self._render(*args, **kwargs)

    def _render(self, text, color, background=None, encoding='utf-8', wrap_length=0, palette=False):

        color, background = convert_to_color(color, background)  # convert to color's

        if encoding not in ('utf-8', 'ascii', 'unicode', 'glyph'):
            raise Exception('valid encodings are {}, not {}'.format('utf-8', 'ascii', 'unicode', 'glyph', encoding))

        if background:
            sdl_surf = self._render_shaded(text, color, background, encoding)
        elif wrap_length:
            if encoding == 'glyph':
                sdl_surf = self._render_blended(text, color, encoding)
            else:
                sdl_surf = self._render_blended_wrapped(text, color, encoding, wrap_length)
        elif palette:
            sdl_surf = self._render_solid(text, color, encoding)
        else:
            sdl_surf = self._render_blended(text, color, encoding)

        if sdl_surf == sdl.ffi.NULL:
            raise SDLError()

        return Surface((sdl_surf.w, sdl_surf.h), surface=sdl_surf)

    def _render_shaded(self, text, color, background, encoding='utf-8'):
        """
        SDL_Surface * TTF_RenderUTF8_Shaded(TTF_Font *font, const char *text, SDL_Color fg, SDL_Color bg);
        SDL_Surface * TTF_RenderText_Shaded(TTF_Font *font, const char *text, SDL_Color fg, SDL_Color bg);
        SDL_Surface * TTF_RenderUNICODE_Shaded(TTF_Font *font, const Uint16 *text, SDL_Color fg, SDL_Color bg);
        SDL_Surface * TTF_RenderGlyph_Shaded(TTF_Font *font, Uint16 ch, SDL_Color fg, SDL_Color bg);
        """
        if encoding == 'utf-8':
            sdl_surf = sdl.ttf.renderUTF8_Shaded(
                self.__sdl_font, utf8(text), color.sdl_color, background.sdl_color)
        elif encoding == 'ascii':
            sdl_surf = sdl.ttf.renderText_Shaded(
                self.__sdl_font, text, color.sdl_color, background.sdl_color)
        elif encoding == 'unicode':
            sdl_surf = sdl.ttf.renderUNICODE_Shaded(
                self.__sdl_font, text, color.sdl_color, background.sdl_color)
        elif encoding == 'glyph':
            sdl_surf = sdl.ttf.renderGlyph_Shaded(
                self.__sdl_font, text, color.sdl_color, background.sdl_color)
        return sdl_surf

    def _render_solid(self, text, color, encoding):
        """
        SDL_Surface * TTF_RenderUTF8_Solid(TTF_Font *font, const char *text, SDL_Color fg);
        SDL_Surface * TTF_RenderText_Solid(TTF_Font *font, const char *text, SDL_Color fg);
        SDL_Surface * TTF_RenderUNICODE_Solid(TTF_Font *font, const Uint16 *text, SDL_Color fg);
        SDL_Surface * TTF_RenderGlyph_Solid(TTF_Font *font, Uint16 ch, SDL_Color fg);
        """
        if encoding == 'utf-8':
            sdl_surf = sdl.ttf.renderUTF8_Solid(self.__sdl_font, utf8(text), color.sdl_color)
        elif encoding == 'ascii':
            sdl_surf = sdl.ttf.renderText_Solid(self.__sdl_font, text, color.sdl_color)
        elif encoding == 'unicode':
            sdl_surf = sdl.ttf.renderUNICODE_Solid(self.__sdl_font, text, color.sdl_color)
        elif encoding == 'glyph':
            sdl_surf = sdl.ttf.renderGlyph_Solid(self.__sdl_font, text, color.sdl_color)
        return sdl_surf

    def _render_blended_wrapped(self, text, color, encoding, wrap_length):
        """
        SDL_Surface * TTF_RenderUTF8_Blended_Wrapped(TTF_Font *font, const char *text, SDL_Color fg, Uint32 wrapLength);
        SDL_Surface * TTF_RenderText_Blended_Wrapped(TTF_Font *font, const char *text, SDL_Color fg, Uint32 wrapLength);
        SDL_Surface * TTF_RenderUNICODE_Blended_Wrapped(TTF_Font *font, const Uint16 *text, SDL_Color fg, Uint32 wrapLength);
        """
        if encoding == 'utf-8':
            sdl_surf = sdl.ttf.renderUTF8_Blended_Wrapped(
                self.__sdl_font, utf8(text), color.sdl_color[0], wrap_length)
        elif encoding == 'ascii':
            sdl_surf = sdl.ttf.renderText_Blended_Wrapped(self.__sdl_font, text, color.sdl_color[0], wrap_length)
        elif encoding == 'unicode':
            sdl_surf = sdl.ttf.renderUNICODE_Blended_Wrapped(self.__sdl_font, text, color.sdl_color[0], wrap_length)
        elif encoding == 'glyph':
            sdl_surf = self._render_blended(text, color, encoding)
        return sdl_surf

    def _render_blended(self, text, color, encoding):
        """
        SDL_Surface * TTF_RenderUTF8_Blended(TTF_Font *font, const char *text, SDL_Color fg);
        SDL_Surface * TTF_RenderText_Blended(TTF_Font *font, const char *text, SDL_Color fg);
        SDL_Surface * TTF_RenderUNICODE_Blended(TTF_Font *font, const Uint16 *text, SDL_Color fg);
        SDL_Surface * TTF_RenderGlyph_Blended(TTF_Font *font, Uint16 ch, SDL_Color fg);
        """
        if encoding == 'utf-8':
            sdl_surf = sdl.ttf.renderUTF8_Blended(self.__sdl_font, utf8(text), color.sdl_color)
        elif encoding == 'ascii':
            sdl_surf = sdl.ttf.renderText_Blended(self.__sdl_font, text, color.sdl_color)
        elif encoding == 'unicode':
            sdl_surf = sdl.ttf.renderUNICODE_Blended(self.__sdl_font, text, color.sdl_color)
        elif encoding == 'glyph':
            sdl_surf = sdl.ttf.renderGlyph_Blended(self.__sdl_font, text, color.sdl_color)
        return sdl_surf

    def size(self, text, encoding='utf-8'):
        """
        TTF_SizeText(TTF_Font *font, const char *text, int *w, int *h)
        TTF_SizeUTF8(TTF_Font *font, const char *text, int *w, int *h)
        TTF_SizeUNICODE(TTF_Font *font, const Uint16 *text, int *w, int *h)
        """
        if encoding == 'utf-8':
            _, w, h = sdl.ttf.sizeUTF8(self.__sdl_font, utf8(text))
        elif encoding == 'ascii':
            _, w, h = sdl.ttf.sizeText(self.__sdl_font, text)
        elif encoding == 'unicode':
            _, w, h = sdl.ttf.sizeUNICODE(self.__sdl_font, text)
        else:
            raise NotImplementedError

        return w, h

    def set_hinting(self, hinting):
        """
        TTF_HINTING_NORMAL = 0
        TTF_HINTING_LIGHT = 1
        TTF_HINTING_MONO = 2
        TTF_HINTING_NONE = 3
        """
        sdl.ttf.setFontHinting(self.__sdl_font, hinting)

    def get_hinting(self):
        return sdl.ttf.getFontHinting(self.sdl_font)

    def set_style(self, style):
        """
        TTF_STYLE_NORMAL        = 0x00
        TTF_STYLE_BOLD          = 0x01
        TTF_STYLE_ITALIC        = 0x02
        TTF_STYLE_UNDERLINE     = 0x04
        TTF_STYLE_STRIKETHROUGH = 0x08
        """
        sdl.ttf.setFontStyle(self.__sdl_font, style)

    def get_style(self):
        return sdl.ttf.getFontStyle(self.__sdl_font)

    def set_outline(self, boolean):
        """
        """
        # TODO: uses same color?
        sdl.ttf.setFontOutline(self.__sdl_font, boolean)

    def get_outline(self):
        return sdl.ttf.getFontOutline(self.__sdl_font) == 1

    def _mask_style_flags(self, boolean, mod_flags):
        flags = self.get_style()
        if boolean:
            flags |= mod_flags
        else:
            flags ^= mod_flags
        return flags

    def set_underline(self, boolean):
        self.set_style(self._mask_style_flags(boolean, TTF_STYLE_UNDERLINE))

    def get_underline(self):
        return self.get_style() & TTF_STYLE_UNDERLINE

    def set_bold(self, boolean):
        self.set_style(self._mask_style_flags(boolean, TTF_STYLE_BOLD))

    def get_bold(self):
        return self.get_style() & TTF_STYLE_BOLD

    def set_italic(self, boolean):
        self.set_style(self._mask_style_flags(boolean, TTF_STYLE_ITALIC))

    def get_italic(self):
        return self.get_style() & TTF_STYLE_ITALIC

    def set_strikethrough(self, boolean):
        self.set_style(self._mask_style_flags(boolean, TTF_STYLE_STRIKETHROUGH))

    def get_strikethrough(self):
        return self.get_style() & TTF_STYLE_STRIKETHROUGH

    def set_normal(self):
        self.set_style(TTF_STYLE_NORMAL)

    def get_normal(self):
        return self.get_style() == TTF_STYLE_NORMAL

    def get_linesize(self):
        return self.get_height() + self.get_ascent() + self.get_descent()

    def get_height(self):
        return sdl.ttf.fontHeight(self.__sdl_font)

    def get_ascent(self):
        return sdl.ttf.fontAscent(self.__sdl_font)

    def get_descent(self):
        return sdl.ttf.fontDescent(self.__sdl_font)

    def get_line_skip(self):
        return sdl.ttf.fontLineSkip(self.__sdl_font)

    def get_kerning(self):
        return sdl.ttf.getFontKerning(self.sdl_font)

    def set_kerning(self, allowed):
        sdl.ttf.setFontKerning(self.__sdl_font, allowed)

    def get_kerning_size(self, prev_index, index):
        """
        int TTF_GetFontKerningSize(TTF_Font *font, int prev_index, int index)
        """
        return sdl.ttf.getFontKerningSize(self.__sdl_font, prev_index, index)

    def get_faces(self):
        return sdl.ttf.fontFaces(self.__sdl_font)

    def is_fixed_width(self):
        return sdl.ttf.fontFaceIsFixedWidth(self.__sdl_font)

    def family_name(self):
        name = sdl.ttf.fontFaceFamilyName(self.__sdl_font)
        return sdl.ffi.string(name).decode('utf-8')

    def style_name(self):
        name = sdl.ttf.fontFaceStyleName(self.__sdl_font)
        return sdl.ffi.string(name).decode('utf-8')

    def glyph_is_provided(self, ch):
        """
        int TTF_GlyphIsProvided(const TTF_Font *font, Uint16 ch)
        """
        return sdl.ttf.glyphIsProvided(self.__sdl_font, ch)

    def metrics(self, ch):
        """get the metrics (dimensions) of a glyph

        To understand what these metrics mean, here is a useful link:
        http://freetype.sourceforge.net/freetype2/docs/tutorial/step2.html
        TTF_GlyphMetrics(TTF_Font *font, Uint16 ch, int *minx, int *maxx, int *miny, int *maxy, int *advance)

        ;return; tuple of int; minx, maxx, miny, maxy, advance
        """
        _, min_x, max_x, min_y, max_y, advance = sdl.ttf.glyphMetrics(self.__sdl_font, ch)
        return min_x, max_x, min_y, max_y, advance

    def filename(self):
        return self.__filename

    def pointsize(self):
        return self.__pointsize

    def close(self):
        if self.__sdl_font:
            sdl.ttf.closeFont(self.__sdl_font)
            self.__sdl_font = None

    def __getsdlfont(self):
        return self.__sdl_font

    sdl_font = property(__getsdlfont)

    def __del__(self):
        self.close()

    def __str__(self):
        return '<{}({}, {}>'.format(self.__class__.__name__, self.__filename, self.__sdl_font.sizeText)


from gsdl2.surface import Surface
