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
_grid_cairo_renderer.py
=======================

Provides
--------

 * GridCairoRenderer: Renders grid slice to Cairo context
 * GridCellCairoRenderer: Renders grid cell to Cairo context
 * GridCellContentCairoRenderer: Renders cell content to Cairo context
 * GridCellBackgroundCairoRenderer: Renders cell background to Cairo context
 * GridCellBorderCairoRenderer: Renders cell border to Cairo context

"""

from src.lib.slicing import slice2range


class GridCairoRenderer(object):
    """Renders a grid slice to a CairoSurface

    Parameters
    ----------

    * context: pycairo.context
    \tThe Cairo context to be drawn to
    * code_array: model.code_array
    \tGrid data structure that yields rendering information
    * slcs: 3 tuple of slice
    \tGrid slice to be printed. May contain multiple tabs

    """

    def __init__(self, context, code_array, slcs):
        self.context = context
        self.code_array = code_array
        self.slcs = slcs

    def get_cell_rect(self, row, col, tab):
        """Returns rectangle of cell on canvas"""

        pos_x = 20 * row
        pos_y = 50 * col
        width = 50
        height = 20

        return pos_x, pos_y, width, height

    def draw(self):
        """Draws slice to context"""

        shape = self.code_array.shape
        row_start, row_stop, row_step = slice2range(self.slcs[0], shape[0])
        col_start, col_stop, col_step = slice2range(self.slcs[1], shape[1])
        tab_start, tab_stop, tab_step = slice2range(self.slcs[2], shape[2])

        for row in xrange(row_start, row_stop, row_step):
            for col in xrange(col_start, col_stop, col_step):
                for tab in xrange(tab_start, tab_stop, tab_step):
                    cell_renderer = GridCellCairoRenderer(
                        self.context,
                        self.code_array,
                        (row, col, tab),
                        self.get_cell_rect(row, col, tab))

                    cell_renderer.draw()


class GridCellCairoRenderer(object):
    """Renders a grid cell to a CairoSurface

    Parameters
    ----------

    * context: pycairo.context
    \tThe Cairo context to be drawn to
    * code_array: model.code_array
    \tGrid data structure that yields rendering information
    * key: 3 tuple of Integer
    \tKey of cell to be rendered
    * rect: 4 tuple of float
    \tx, y, width and height of cell rectangle

    """

    def __init__(self, context, code_array, key, rect):
        self.context = context
        self.code_array = code_array
        self.key = key
        self.rect = rect

    def draw(self):
        """Draws cell to context"""

        cell_background_renderer = GridCellBackgroundCairoRenderer(
            self.context,
            self.code_array,
            self.key,
            self.rect)

        cell_content_renderer = GridCellContentCairoRenderer(
            self.context,
            self.code_array,
            self.key,
            self.rect)

        cell_border_renderer = GridCellBorderCairoRenderer(
            self.context,
            self.code_array,
            self.key,
            self.rect)

        cell_background_renderer.draw()
        cell_content_renderer.draw()
        cell_border_renderer.draw()


class GridCellContentCairoRenderer(object):
    """Renders cell content to Cairo context

    Parameters
    ----------

    * context: pycairo.context
    \tThe Cairo context to be drawn to
    * code_array: model.code_array
    \tGrid data structure that yields rendering information
    * key: 3 tuple of Integer
    \tKey of cell to be rendered

    """

    def __init__(self, context, code_array, key, rect):
        self.context = context
        self.code_array = code_array
        self.key = key
        self.rect = rect

    def draw(self):
        """Draws cell content to context"""

        pass


class GridCellBackgroundCairoRenderer(object):
    """Renders cell background to Cairo context

    Parameters
    ----------

    * context: pycairo.context
    \tThe Cairo context to be drawn to
    * code_array: model.code_array
    \tGrid data structure that yields rendering information
    * key: 3 tuple of Integer
    \tKey of cell to be rendered

    """

    def __init__(self, context, code_array, key, rect):
        self.context = context
        self.code_array = code_array
        self.key = key
        self.rect = rect

    def draw(self):
        """Draws cell background to context"""

        pass


class GridCellBorderCairoRenderer(object):
    """Renders cell border to Cairo context

    Parameters
    ----------

    * context: pycairo.context
    \tThe Cairo context to be drawn to
    * code_array: model.code_array
    \tGrid data structure that yields rendering information
    * key: 3 tuple of Integer
    \tKey of cell to be rendered

    """

    def __init__(self, context, code_array, key, rect):
        self.context = context
        self.code_array = code_array
        self.cell_attributes = code_array.cell_attributes
        self.key = key
        self.rect = rect

    def _get_bottom_line_coordinates(self):
        """Returns start and stop coordinates of bottom line"""

        rect_x, rect_y, rect_width, rect_height = self.rect

        start_point = rect_x, rect_y + rect_height
        end_point = rect_x + rect_width, rect_y + rect_height

        return start_point, end_point

    def _get_right_line_coordinates(self):
        """Returns start and stop coordinates of right line"""

        rect_x, rect_y, rect_width, rect_height = self.rect

        start_point = rect_x + rect_width, rect_y
        end_point = rect_x + rect_width, rect_y + rect_height

        return start_point, end_point

    def _get_bottom_line_color(self):
        """Returns color rgba tuple of bottom line"""

        pass

    def _get_right_line_color(self):
        """Returns color rgba tuple of right line"""

        pass

    def _get_bottom_line_width(self):
        """Returns width of bottom line"""

        pass

    def _get_right_line_width(self):
        """Returns width of right line"""

        pass

    def draw(self):
        """Draws cell border to context"""

        # Bottom line

        bl_start_point, bl_end_point = self._get_bottom_line_coordinates()
        self.context.move_to(bl_start_point[0], bl_start_point[1])
        self.context.line_to(bl_end_point[0], bl_end_point[1])
        self.context.stroke()

        # Right line

        rl_start_point, rl_end_point = self._get_right_line_coordinates()
        self.context.move_to(rl_start_point[0], rl_start_point[1])
        self.context.line_to(rl_end_point[0], rl_end_point[1])
        self.context.stroke()
