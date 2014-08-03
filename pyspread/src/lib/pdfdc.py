#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright Martin Manns
# Distributed under the terms of the GNU General Public License

# --------------------------------------------------------------------
# pyspread is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyspread is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyspread.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

"""
pdfdc.py
========

Draw context for generating PDF files with Cairo

TODO: After some tests I come to the conclusion that it is easier to
      rewrite the renderer than to create an artificial Cairo dc

"""

import math

import cairo
import pango
import pangocairo
import wx


try:
    from src.config import config
    MAX_RESULT_LENGTH = config["max_result_length"]
except ImportError:
    MAX_RESULT_LENGTH = 100000


class PdfDC(object):
    """Draw context for Cairo based PDF writing"""

    paper_inch_sizes = {
        "A4": (8.267, 11.692),
        "Letter": (8.5, 11.0),
    }

    def __init__(self, filepath, papertype="A4"):

        if papertype is not None:
            width_inch, height_inch = self.paper_inch_sizes[papertype]
            self.width = width_inch * 72.0
            self.height = height_inch * 72.0
        else:
            raise NotImplementedError("Custom paper size not implemented")

        surface = cairo.PDFSurface(filepath, self.width, self.height)
        self.ctx = cairo.Context(surface)
        self.ptx = pangocairo.CairoContext(self.ctx)
        self.pango_layout = self.ptx.create_layout()  # Reset by DrawText

    def _wxcolor2rgba(self, colour):
        """Returns rgba list from wx.Colour"""

        rgb = [c / 255.0 for c in colour.Get()]

        if len(rgb) == 3:
            rgb += [1]
        elif len(rgb) != 4:
            raise ValueError("Colour does not yield 3 or 4 rgb values")

        return rgb

    # State preparation

    def SelectObject(self, text):
        pass

    def SetDeviceOrigin(self, text):
        pass

    def SetBackgroundMode(self, text):
        pass

    def SetTextForeground(self, colour):
        """Sets stroke from wx.Colour"""

        rgba = self._wxcolor2rgba(colour)
        self.ctx.set_source_rgba(*rgba)

    def SetBrush(self, brush):
        """Sets color (only!) from brush"""

        colour = brush.Colour
        rgba = self._wxcolor2rgba(colour)
        self.ctx.set_source_rgba(*rgba)

    def SetPen(self, pen):
        """Sets color and line width from pen"""

        color = pen.Colour
        rgb = [c / 255.0 for c in color.Get()]
        if len(rgb) == 3:
            self.ctx.set_source_rgb(*rgb)
        elif len(rgb) == 4:
            self.ctx.set_source_rgba(*rgb)
        else:
            raise ValueError("Colour does not yield 3 or 4 rgb values")

        width = pen.GetWidth()
        self.ctx.set_line_width(width / 4.0)

    def SetFont(self, font):
        """Sets wx.Font to pango layout"""

        wx2pango_weights = {
            wx.FONTWEIGHT_BOLD: pango.WEIGHT_BOLD,
            wx.FONTWEIGHT_LIGHT: pango.WEIGHT_LIGHT,
            wx.FONTWEIGHT_NORMAL: pango.WEIGHT_NORMAL,
        }

        wx2pango_styles = {
            wx.FONTSTYLE_NORMAL: pango.STYLE_NORMAL,
            wx.FONTSTYLE_SLANT: pango.STYLE_OBLIQUE,
            wx.FONTSTYLE_ITALIC: pango.STYLE_ITALIC,
        }

        name = font.GetFaceName()
        size = font.GetPointSize()

        font_description = pango.FontDescription(" ".join([name, str(size)]))
        self.pango_layout.set_font_description(font_description)

        attrs = pango.AttrList()

        # Underline
        underline = font.GetUnderlined()
        attrs.insert(pango.AttrUnderline(underline, 0, MAX_RESULT_LENGTH))

        # Weight
        weight = wx2pango_weights[font.GetWeight()]
        attrs.insert(pango.AttrWeight(weight, 0, MAX_RESULT_LENGTH))

        # Style
        style = wx2pango_styles[font.GetStyle()]
        attrs.insert(pango.AttrStyle(style, 0, MAX_RESULT_LENGTH))

        self.pango_layout.set_attributes(attrs)

    def SetClippingRect(self, rect):
        """Clips the context to rect and saves the old clipping state"""

        self.ctx.save()
        self.ctx.rectangle(rect.x, rect.y, rect.width, rect.height)
        self.ctx.clip()

    def DestroyClippingRegion(self):
        """Reverts saved clipping state"""

        self.ctx.restore()

    # Drawing

    def BeginDrawing(self):
        pass

    def EndDrawing(self):
        pass

    def DrawLine(self, x1, y1, x2, y2):
        """Draws a line from x1,y2 to x2, y2"""

        self.ctx.move_to(x1, y1)
        self.ctx.line_to(x2, y2)
        self.ctx.stroke()

    def DrawLineList(self, lines, pens):
        """Draws a line list"""

        for line, pen in zip(lines, pens):
            self.SetPen(pen)
            x1, y1, x2, y2 = line
            self.DrawLine(x1, y1, x2, y2)

    def DrawRotatedText(self, text, x, y, angle):
        """Draws rotated text"""

        rad_angle = -angle / 180.0 * math.pi

        self.ctx.translate(x, y)
        self.ctx.rotate(rad_angle)

        self.pango_layout.set_text(text)
        self.ptx.update_layout(self.pango_layout)
        self.ptx.show_layout(self.pango_layout)

        self.pango_layout = self.ptx.create_layout()

        self.ctx.rotate(-rad_angle)
        self.ctx.translate(-x, -y)

    def DrawPolygonList(self, point_list, pens=None, brushes=None):
        """Not implemented - only used for cursor that shall not be drawn"""

        pass

    def DrawBitmap(self, bmp, x, y, useMask):
        pass

    def Blit(self, xdest, ydest, width, height, source, xsrc, ysrc, rop):

        pass

    def DrawRectangle(self, x, y, width, height):
        """Draws a rectangle"""

        self.ctx.rectangle(x, y, width, height)
        self.ctx.fill()

    # Auxilliaries

    def GetFullTextExtent(self, text):
        """Returns logical text extent"""

        self.pango_layout.set_text(text)
        return self.pango_layout.get_extents()[1]

    GetTextExtent = GetFullTextExtent

    def GetPartialTextExtents(self, text):
        """Returns physical text extent"""

        extents = []

        for i in xrange(len(text)):
            self.pango_layout.set_text(text[:i+1])
            extents.append(self.pango_layout.get_extents()[0][0])

        return extents

    def show_page(self):
        """Writes a page to tyhe pdf file"""

        self.ctx.show_page()

if __name__ == "__main__":
    dc = PdfDC("test/test.pdf")
    app = wx.App()

    dc.SetBrush(wx.Brush(wx.Colour(0, 0, 255)))
    dc.DrawRectangle(10, 10, dc.width-20, dc.height-20)

    dc.SetPen(wx.Pen(wx.Colour(200, 34, 235), 2))
    dc.DrawLine(10, 10, 70, 90)

    linelist = [(90, 90, 200, i*3) for i in xrange(100)]
    penlist = [wx.Pen(wx.Colour(0, i*2, i*2), 1) for i in xrange(100)]
    dc.DrawLineList(linelist, penlist)

    dc.SetTextForeground(wx.Colour(255, 255, 0))
    textfont = wx.Font(50, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC,
                       wx.FONTWEIGHT_BOLD, 0, 'Deja Vu Serif')
    dc.SetFont(textfont)

    dc.DrawRotatedText("Test", 100, 250, 10)

    textfont = wx.Font(50, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                       wx.FONTWEIGHT_NORMAL, 0, 'Deja Vu Serif')
    dc.SetFont(textfont)
    dc.DrawRotatedText("Test2", 300, 250, 0)

    dc.show_page()
