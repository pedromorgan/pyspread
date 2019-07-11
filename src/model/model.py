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

.. _layers:

`model.py` contains the core data structures of pyspread.
It is divided into the following layers.

- Layer 3: :class:`~model.model.CodeArray`
- Layer 2: :class:`~model.model.DataArray`
- Layer 1: :class:`~model.model.DictGrid`
- Layer 0: KeyValueStore

"""
from __future__ import absolute_import
from builtins import filter
from builtins import str
from builtins import zip
from builtins import range
from builtins import object

import ast
import base64
import bz2
from matplotlib.figure import Figure
from collections import defaultdict
from copy import copy
import datetime
from inspect import isgenerator
from itertools import product
import re
import sys

import numpy
#from PyQt5.QtGui import QImage, QPixmap

from settings import Settings

from lib.typechecks import isslice, isstring
from lib.selection import Selection

from .unredo import UnRedo


class CellAttributes(list):
    """Stores cell formatting attributes in a tuple with three elements

    - The first element of each tuple is a :class:`Selection`
    - The second element is the table
    - The third element is a `dict` of attributes that are altered

    This class provides attribute read access to single cells
    via `__getitem__`, otherwise it behaves similar to a list.

    Note that for the method :class:`~model.model.CellAttributes.undoable_append` to work, unredo
    has to be defined as class attribute.

    """

    settings = Settings()

    default_cell_attributes = {
        "borderwidth_bottom": 1,
        "borderwidth_right": 1,
        "bordercolor_bottom": settings.grid_color,
        "bordercolor_right": settings.grid_color,
        "bgcolor": settings.background_color,
        "textfont": settings.font,
        "pointsize": 10,
        "fontweight": 50,
        "fontstyle": 0,
        "textcolor": settings.text_color,
        "underline": False,
        "strikethrough": False,
        "locked": False,
        "angle": 0.0,
        "column-width": 75,
        "row-height": 26,
        "vertical_align": "align_top",
        "justification": "justify_left",
        "frozen": False,
        "merge_area": None,
        "renderer": "text",
        "button_cell": False,
        "panel_cell": False,
        "video_volume": None,
    }

    # Cache for __getattr__ maps key to tuple of len and attr_dict

    _attr_cache = {}
    _table_cache = {}

    def undoable_append(self, value, mark_unredo=True):
        """Appends item to list and provides undo and redo functionality"""

        undo_operation = (self.pop, [])
        redo_operation = (self.undoable_append, [value, mark_unredo])

        self.unredo.append(undo_operation, redo_operation)

        if mark_unredo:
            self.unredo.mark()

        self.append(value)
        self._attr_cache.clear()

        sel, tab, val = value

    def __getitem__(self, key):
        """Returns attribute dict for a single key"""

        assert not any(type(key_ele) is slice for key_ele in key)

        if key in self._attr_cache:
            cache_len, cache_dict = self._attr_cache[key]

            # Use cache result only if no new attrs have been defined
            if cache_len == len(self):
                return cache_dict

        # Update table cache if it is outdated (e.g. when creating a new grid)
        if len(self) != self._len_table_cache():
            self._update_table_cache()

        row, col, tab = key

        result_dict = copy(self.default_cell_attributes)

        try:
            for selection, attr_dict in self._table_cache[tab]:
                if (row, col) in selection:
                    result_dict.update(attr_dict)
        except KeyError:
            pass

        # Upddate cache with current length and dict
        self._attr_cache[key] = (len(self), result_dict)

        return result_dict

    def _len_table_cache(self):
        """Returns the length of the table cache"""

        length = 0

        for table in self._table_cache:
            length += len(self._table_cache[table])

        return length

    def _update_table_cache(self):
        """Clears and updates the table cache to be in sync with self"""

        self._table_cache.clear()
        for sel, tab, val in self:
            try:
                self._table_cache[tab].append((sel, val))
            except KeyError:
                self._table_cache[tab] = [(sel, val)]

        assert len(self) == self._len_table_cache()

    def get_merging_cell(self, key):
        """Returns key of cell that merges the cell key

        or None if cell key not merged

        Parameters
        ----------
        key: 3-tuple of Integer
        \tThe key of the cell that is merged

        """

        row, col, tab = key

        # Is cell merged
        merge_area = self[key]["merge_area"]

        if merge_area:
            return merge_area[0], merge_area[1], tab

    # Allow getting and setting elements in list
    get_item = list.__getitem__
    set_item = list.__setitem__

# End of class CellAttributes


class DictGrid(dict):
    """The core data class with all information that is stored in a `.pys` file.

    Besides grid code access via standard dict operations, it provides
    the following attributes:

    * :class:`~model.model.DictGrid.cell_attributes`: Stores cell formatting attributes
    * :class:`~model.model.DictGrid.macros`: String of all macros

    This class represents layer 1 of the model.

    Parameters
    ----------
    shape: n-tuple of integer
    \tShape of the grid

    :param shape: n-tuple of integer
    :type shape: tuple

    """

    def __init__(self, shape):
        super().__init__()

        self.shape = shape

        self.cell_attributes = CellAttributes()
        """Stores cell formatting attributes"""

        self.macros = u""
        """String of all macros"""

        self.row_heights = defaultdict(float)  # Keys have format (row, table)
        self.col_widths = defaultdict(float)  # Keys have format (col, table)

    def __getitem__(self, key):

        shape = self.shape

        for axis, key_ele in enumerate(key):
            if shape[axis] <= key_ele or key_ele < -shape[axis]:
                msg = "Grid index {key} outside grid shape {shape}."
                msg = msg.format(key=key, shape=shape)
                raise IndexError(msg)

        return super().__getitem__(key)

    def __missing__(self, key):
        """Default value is None"""

        return

# End of class DictGrid

# -----------------------------------------------------------------------------


class DataArray(object):
    """DataArray provides enhanced grid read/write access.

    Enhancements comprise:
     * Slicing
     * Multi-dimensional operations such as insertion and deletion along 1 axis
     * Undo/redo operations

    This class represents layer 2 of the model.

    :param shape: Shape of the grid
    :type shape: n-tuple of integer

    """

    settings = Settings()

    def __init__(self, shape):
        self.dict_grid = DictGrid(shape)

        # Undo and redo management
        self.unredo = UnRedo()
        self.dict_grid.cell_attributes.unredo = self.unredo

        # Safe mode
        self.safe_mode = False

    def __eq__(self, other):
        if not hasattr(other, "dict_grid") or \
           not hasattr(other, "cell_attributes"):
            return NotImplemented

        return self.dict_grid == other.dict_grid and \
            self.cell_attributes == other.cell_attributes

    def __ne__(self, other):
        return not self.__eq__(other)

    # Data is the central content interface for loading / saving data.
    # It shall be used for loading and saving from and to pys and other files.
    # It shall be used for loading and saving macros.
    # It is not used for importing and exporting data because these operations
    # are partial to the grid.

    @property
    def data(self):
        """Returns dict of data content.

        Keys
        ----

        shape: 3-tuple of Integer
        \tGrid shape
        grid: Dict of 3-tuples to strings
        \tCell content
        attributes: List of 3-tuples
        \tCell attributes
        row_heights: Dict of 2-tuples to float
        \t(row, tab): row_height
        col_widths: Dict of 2-tuples to float
        \t(col, tab): col_width
        macros: String
        \tMacros from macro list

        """

        data = {}

        data["shape"] = self.shape
        data["grid"] = {}.update(self.dict_grid)
        data["attributes"] = [ca for ca in self.cell_attributes]
        data["row_heights"] = self.row_heights
        data["col_widths"] = self.col_widths
        data["macros"] = self.macros

        return data

    @data.setter
    def data(self, **kwargs):
        """Sets data from given parameters

        Old values are deleted.
        If a paremeter is not given, nothing is changed.

        Parameters
        ----------

        shape: 3-tuple of Integer
        \tGrid shape
        grid: Dict of 3-tuples to strings
        \tCell content
        attributes: List of 3-tuples
        \tCell attributes
        row_heights: Dict of 2-tuples to float
        \t(row, tab): row_height
        col_widths: Dict of 2-tuples to float
        \t(col, tab): col_width
        macros: String
        \tMacros from macro list

        """

        if "shape" in kwargs:
            self.shape = kwargs["shape"]

        if "grid" in kwargs:
            self.dict_grid.clear()
            self.dict_grid.update(kwargs["grid"])

        if "attributes" in kwargs:
            self.attributes[:] = kwargs["attributes"]

        if "row_heights" in kwargs:
            self.row_heights = kwargs["row_heights"]

        if "col_widths" in kwargs:
            self.col_widths = kwargs["col_widths"]

        if "macros" in kwargs:
            self.macros = kwargs["macros"]

    @property
    def row_heights(self):
        """row_heights interface to dict_grid"""

        return self.dict_grid.row_heights

    @row_heights.setter
    def _row_heights(self, row_heights):
        """row_heights interface to dict_grid"""

        self.dict_grid.row_heights = row_heights

    @property
    def col_widths(self):
        """col_widths interface to dict_grid"""

        return self.dict_grid.col_widths

    @col_widths.setter
    def col_widths(self, col_widths):
        """col_widths interface to dict_grid"""

        self.dict_grid.col_widths = col_widths

    @property
    def cell_attributes(self):
        """cell_attributes interface to dict_grid"""

        return self.dict_grid.cell_attributes

    @cell_attributes.setter
    def cell_attributes(self, value):
        """cell_attributes interface to dict_grid"""

        # First empty cell_attributes
        self.cell_attributes[:] = []
        self.cell_attributes.extend(value)

    @property
    def macros(self):
        """macros interface to dict_grid"""

        return self.dict_grid.macros

    @macros.setter
    def macros(self, macros):
        """Sets  macros string"""

        self.dict_grid.macros = macros

    @property
    def shape(self):
        """Returns dict_grid shape"""

        return self.dict_grid.shape

    def _set_shape(self, shape, mark_unredo=True):
        """Deletes all cells beyond new shape and sets dict_grid shape

        Parameters
        ----------
        shape: 3-tuple of Integer
        \tTarget shape for grid
        mark_unredo: Boolean, defaults to True
        \tIf True then an unredo marker is set after the operation

        """

        # Delete each cell that is beyond new borders

        old_shape = self.shape

        if any(new_axis < old_axis
               for new_axis, old_axis in zip(shape, old_shape)):
            for key in list(self.dict_grid.keys()):
                if any(key_ele >= new_axis
                       for key_ele, new_axis in zip(key, shape)):
                    self.pop(key)

        # Set dict_grid shape attribute

        self.dict_grid.shape = shape

        # UnRedo support

        undo_operation = (self._set_shape, [old_shape, mark_unredo])
        redo_operation = (self._set_shape, [shape, mark_unredo])

        self.unredo.append(undo_operation, redo_operation)

        if mark_unredo:
            self.unredo.mark()

        # End UnRedo support

    @shape.setter
    def shape(self, shape):
        self._set_shape(shape)

    def __iter__(self):
        """Returns iterator over self.dict_grid"""

        return iter(self.dict_grid)

    # Slice support

    def __getitem__(self, key):
        """Adds slicing access to cell code retrieval

        The cells are returned as a generator of generators, of ... of unicode.

        Parameters
        ----------
        key: n-tuple of integer or slice
        \tKeys of the cell code that is returned

        Note
        ----
        Classical Excel type addressing (A$1, ...) may be added here

        """

        for key_ele in key:
            if isslice(key_ele):
                # We have something slice-like here

                return self.cell_array_generator(key)

            elif isstring(key_ele):
                # We have something string-like here
                msg = "Cell string based access not implemented"
                raise NotImplementedError(msg)

        # key_ele should be a single cell

        return self.dict_grid[key]

    def __setitem__(self, key, value, mark_unredo=True):
        """Accepts index and slice keys

        Parameters
        ----------
        key: 3-tuple of Integer or Slice object
        \tCell key(s) that shall be set
        value: Object (should be Unicode or similar)
        \tCode for cell(s) to be set
        mark_unredo: Boolean, defaults to True
        \tIf True then an unredo marker is set after the operation

        """

        single_keys_per_dim = []

        for axis, key_ele in enumerate(key):
            if isslice(key_ele):
                # We have something slice-like here

                length = key[axis]
                slice_range = range(*key_ele.indices(length))
                single_keys_per_dim.append(slice_range)

            elif isstring(key_ele):
                # We have something string-like here

                raise NotImplementedError

            else:
                # key_ele is a single cell

                single_keys_per_dim.append((key_ele, ))

        single_keys = product(*single_keys_per_dim)

        unredo_mark = False

        for single_key in single_keys:
            if value:
                # UnRedo support

                old_value = self(key)

                try:
                    old_value = str(old_value, encoding="utf-8")
                except TypeError:
                    pass

                # We seem to have double calls on __setitem__
                # This hack catches them

                if old_value != value:

                    unredo_mark = True

                    undo_operation = (self.__setitem__,
                                      [key, old_value, mark_unredo])
                    redo_operation = (self.__setitem__,
                                      [key, value, mark_unredo])

                    self.unredo.append(undo_operation, redo_operation)

                    # End UnRedo support

                # Never change merged cells
                merging_cell = \
                    self.cell_attributes.get_merging_cell(single_key)
                if merging_cell is None or merging_cell == single_key:
                    self.dict_grid[single_key] = value
            else:
                # Value is empty --> delete cell
                try:
                    self.pop(key)

                except (KeyError, TypeError):
                    pass

        if mark_unredo and unredo_mark:
            self.unredo.mark()

    # Pickle support

    def __getstate__(self):
        """Returns dict_grid for pickling

        Note that all persistent data is contained in the DictGrid class

        """

        return {"dict_grid": self.dict_grid}

    def get_row_height(self, row, tab):
        """Returns row height"""

        try:
            return self.row_heights[(row, tab)]

        except KeyError:
            return self.settings.default_row_height

    def get_col_width(self, col, tab):
        """Returns column width"""

        try:
            return self.col_widths[(col, tab)]

        except KeyError:
            return self.settings.default_col_width

    def keys(self):
        """Returns keys in self.dict_grid"""

        return list(self.dict_grid.keys())

    def pop(self, key, mark_unredo=True):
        """Pops dict_grid with undo and redo support

        Parameters
        ----------
        key: 3-tuple of Integer
        \tCell key that shall be popped
        mark_unredo: Boolean, defaults to True
        \tIf True then an unredo marker is set after the operation

        """

        result = self.dict_grid.pop(key)

        # UnRedo support

        if mark_unredo:
            self.unredo.mark()

        undo_operation = (self.__setitem__, [key, result, mark_unredo])
        redo_operation = (self.pop, [key, mark_unredo])

        self.unredo.append(undo_operation, redo_operation)

        if mark_unredo:
            self.unredo.mark()

        # End UnRedo support

        return result

    def get_last_filled_cell(self, table=None):
        """Returns key for the bottommost rightmost cell with content

        Parameters
        ----------
        table: Integer, defaults to None
        \tLimit search to this table

        """

        maxrow = 0
        maxcol = 0

        for row, col, tab in self.dict_grid:
            if table is None or tab == table:
                maxrow = max(row, maxrow)
                maxcol = max(col, maxcol)

        return maxrow, maxcol, table

    def cell_array_generator(self, key):
        """Generator traversing cells specified in key

        Parameters
        ----------
        key: Iterable of Integer or slice
        \tThe key specifies the cell keys of the generator

        """

        for i, key_ele in enumerate(key):

            # Get first element of key that is a slice
            if type(key_ele) is slice:
                slc_keys = range(*key_ele.indices(self.dict_grid.shape[i]))
                key_list = list(key)

                key_list[i] = None

                has_subslice = any(type(ele) is slice for ele in key_list)

                for slc_key in slc_keys:
                    key_list[i] = slc_key

                    if has_subslice:
                        # If there is a slice left yield generator
                        yield self.cell_array_generator(key_list)

                    else:
                        # No slices? Yield value
                        yield self[tuple(key_list)]

                break

    def _shift_rowcol(self, insertion_point, no_to_insert, mark_unredo):
        """Shifts row and column sizes when a table is inserted or deleted"""

        if mark_unredo:
            self.unredo.mark()

        # Shift row heights

        new_row_heights = {}
        del_row_heights = []

        for row, tab in self.row_heights:
            if tab > insertion_point:
                new_row_heights[(row, tab + no_to_insert)] = \
                    self.row_heights[(row, tab)]
                del_row_heights.append((row, tab))

        for row, tab in new_row_heights:
            self.set_row_height(row, tab, new_row_heights[(row, tab)],
                                mark_unredo=False)

        for row, tab in del_row_heights:
            if (row, tab) not in new_row_heights:
                self.set_row_height(row, tab, None, mark_unredo=False)

        # Shift column widths

        new_col_widths = {}
        del_col_widths = []

        for col, tab in self.col_widths:
            if tab > insertion_point:
                new_col_widths[(col, tab + no_to_insert)] = \
                    self.col_widths[(col, tab)]
                del_col_widths.append((col, tab))

        for col, tab in new_col_widths:
            self.set_col_width(col, tab, new_col_widths[(col, tab)],
                               mark_unredo=False)

        for col, tab in del_col_widths:
            if (col, tab) not in new_col_widths:
                self.set_col_width(col, tab, None, mark_unredo=False)

        if mark_unredo:
            self.unredo.mark()

    def _adjust_rowcol(self, insertion_point, no_to_insert, axis, tab=None,
                       mark_unredo=True):
        """Adjusts row and column sizes on insertion/deletion"""

        if axis == 2:
            self._shift_rowcol(insertion_point, no_to_insert, mark_unredo)
            return

        assert axis in (0, 1)

        if mark_unredo:
            self.unredo.mark()

        cell_sizes = self.col_widths if axis else self.row_heights
        set_cell_size = self.set_col_width if axis else self.set_row_height

        new_sizes = {}
        del_sizes = []

        for pos, table in cell_sizes:
            if pos > insertion_point and (tab is None or tab == table):
                if 0 <= pos + no_to_insert < self.shape[axis]:
                    new_sizes[(pos + no_to_insert, table)] = \
                        cell_sizes[(pos, table)]
                del_sizes.append((pos, table))

        for pos, table in new_sizes:
            set_cell_size(pos, table, new_sizes[(pos, table)],
                          mark_unredo=False)

        for pos, table in del_sizes:
            if (pos, table) not in new_sizes:
                set_cell_size(pos, table, None, mark_unredo=False)

        if mark_unredo:
            self.unredo.mark()

    def _adjust_merge_area(self, attrs, insertion_point, no_to_insert, axis):
        """Returns an updated merge area

        Parameters
        ----------
        attrs: Dict
        \tCell attribute dictionary that shall be adjusted
        insertion_point: Integer
        \tPont on axis, before which insertion takes place
        no_to_insert: Integer >= 0
        \tNumber of rows/cols/tabs that shall be inserted
        axis: Integer in range(2)
        \tSpecifies number of dimension, i.e. 0 == row, 1 == col

        """

        assert axis in range(2)

        if "merge_area" not in attrs or attrs["merge_area"] is None:
            return

        top, left, bottom, right = attrs["merge_area"]
        selection = Selection([(top, left)], [(bottom, right)], [], [], [])
        selection.insert(insertion_point, no_to_insert, axis)
        __top, __left = selection.block_tl[0]
        __bottom, __right = selection.block_br[0]

        # Adjust merge area if it is beyond the grid shape
        rows, cols, tabs = self.shape

        if __top < 0 or __bottom >= rows or __left < 0 or __right >= cols:
            attrs["merge_area"] = None
        else:
            attrs["merge_area"] = __top, __left, __bottom, __right

    def _adjust_cell_attributes(self, insertion_point, no_to_insert, axis,
                                tab=None, cell_attrs=None, mark_unredo=True):
        """Adjusts cell attributes on insertion/deletion

        Parameters
        ----------
        insertion_point: Integer
        \tPont on axis, before which insertion takes place
        no_to_insert: Integer >= 0
        \tNumber of rows/cols/tabs that shall be inserted
        axis: Integer in range(3)
        \tSpecifies number of dimension, i.e. 0 == row, 1 == col, ...
        tab: Integer, defaults to None
        \tIf given then insertion is limited to this tab for axis < 2
        cell_attrs: List, defaults to []
        \tIf not empty then the given cell attributes replace the existing ones
        mark_unredo: Boolean, defaults to True
        \tIf True then an unredo marker is set after the operation

        """

        def replace_cell_attributes_table(index, new_table):
            ca = list(self.cell_attributes.get_item(index))
            ca[1] = new_table
            self.cell_attributes.set_item(index, tuple(ca))

        if axis not in list(range(3)):
            raise ValueError("Axis must be in [0, 1, 2]")

        assert tab is None or tab >= 0

        if cell_attrs is None:
            cell_attrs = []

        # Store existing cell attributes for creating undo operation
        old_cell_attrs = self.cell_attributes[:]

        if cell_attrs:
            self.cell_attributes[:] = cell_attrs

        elif axis < 2:
            # Adjust selections on given table

            for selection, table, attrs in self.cell_attributes:
                if tab is None or tab == table:
                    selection.insert(insertion_point, no_to_insert, axis)
                    # Update merge area if present
                    self._adjust_merge_area(attrs, insertion_point,
                                            no_to_insert, axis)

        elif axis == 2:
            # Adjust tabs

            pop_indices = []

            for i, cell_attribute in enumerate(self.cell_attributes):
                selection, table, value = cell_attribute

                if no_to_insert < 0 and insertion_point <= table:
                    if insertion_point > table + no_to_insert:
                        # Delete later
                        pop_indices.append(i)
                    else:
                        replace_cell_attributes_table(i, table + no_to_insert)

                elif insertion_point < table:
                    # Insert
                    replace_cell_attributes_table(i, table + no_to_insert)

            for i in pop_indices[::-1]:
                self.cell_attributes.pop(i)

        self.cell_attributes._attr_cache.clear()
        self.cell_attributes._update_table_cache()

        undo_operation = (self._adjust_cell_attributes,
                          [insertion_point, -no_to_insert, axis, tab,
                           old_cell_attrs, mark_unredo])
        redo_operation = (self._adjust_cell_attributes,
                          [insertion_point, no_to_insert, axis, tab,
                           cell_attrs, mark_unredo])

        self.unredo.append(undo_operation, redo_operation)

        if mark_unredo:
            self.unredo.mark()

    def insert(self, insertion_point, no_to_insert, axis, tab=None):
        """Inserts no_to_insert rows/cols/tabs/... before insertion_point

        Parameters
        ----------

        insertion_point: Integer
        \tPont on axis, before which insertion takes place
        no_to_insert: Integer >= 0
        \tNumber of rows/cols/tabs that shall be inserted
        axis: Integer
        \tSpecifies number of dimension, i.e. 0 == row, 1 == col, ...
        tab: Integer, defaults to None
        \tIf given then insertion is limited to this tab for axis < 2

        """

        self.unredo.mark()

        if not 0 <= axis <= len(self.shape):
            raise ValueError("Axis not in grid dimensions")

        if insertion_point > self.shape[axis] or \
           insertion_point < -self.shape[axis]:
            raise IndexError("Insertion point not in grid")

        new_keys = {}
        del_keys = []

        for key in list(self.dict_grid.keys()):
            if key[axis] > insertion_point and (tab is None or tab == key[2]):
                new_key = list(key)
                new_key[axis] += no_to_insert
                if 0 <= new_key[axis] < self.shape[axis]:
                    new_keys[tuple(new_key)] = self(key)
                del_keys.append(key)

        # Now re-insert moved keys

        for key in del_keys:
            if key not in new_keys and self(key) is not None:
                self.pop(key, mark_unredo=False)

        self._adjust_rowcol(insertion_point, no_to_insert, axis, tab=tab,
                            mark_unredo=False)
        self._adjust_cell_attributes(insertion_point, no_to_insert, axis,
                                     tab, mark_unredo=False)

        for key in new_keys:
            self.__setitem__(key, new_keys[key], mark_unredo=False)

        self.unredo.mark()

    def delete(self, deletion_point, no_to_delete, axis, tab=None):
        """Deletes no_to_delete rows/cols/... starting with deletion_point

        Axis specifies number of dimension, i.e. 0 == row, 1 == col, 2 == tab

        """

        self.unredo.mark()

        if not 0 <= axis < len(self.shape):
            raise ValueError("Axis not in grid dimensions")

        if no_to_delete < 0:
            raise ValueError("Cannot delete negative number of rows/cols/...")

        elif no_to_delete >= self.shape[axis]:
            raise ValueError("Last row/column/table must not be deleted")

        if deletion_point > self.shape[axis] or \
           deletion_point <= -self.shape[axis]:
            raise IndexError("Deletion point not in grid")

        new_keys = {}
        del_keys = []

        # Note that the loop goes over a list that copies all dict keys
        for key in list(self.dict_grid.keys()):
            if tab is None or tab == key[2]:
                if deletion_point <= key[axis] < deletion_point + no_to_delete:
                    del_keys.append(key)

                elif key[axis] >= deletion_point + no_to_delete:
                    new_key = list(key)
                    new_key[axis] -= no_to_delete

                    new_keys[tuple(new_key)] = self(key)
                    del_keys.append(key)

        # Now re-insert moved keys

        for key in new_keys:
            self.__setitem__(key, new_keys[key], mark_unredo=False)

        for key in del_keys:
            if key not in new_keys and self(key) is not None:
                self.pop(key, mark_unredo=False)

        self._adjust_rowcol(deletion_point, -no_to_delete, axis, tab=tab,
                            mark_unredo=False)
        self._adjust_cell_attributes(deletion_point, -no_to_delete, axis,
                                     tab, mark_unredo=False)

        self.unredo.mark()

    def set_row_height(self, row, tab, height, mark_unredo=True):
        """Sets row height"""

        if mark_unredo:
            self.unredo.mark()

        try:
            old_height = self.row_heights.pop((row, tab))

        except KeyError:
            old_height = None

        if height is not None:
            self.row_heights[(row, tab)] = float(height)

        # Make undoable

        undo_operation = (self.set_row_height,
                          [row, tab, old_height, mark_unredo])
        redo_operation = (self.set_row_height, [row, tab, height, mark_unredo])

        self.unredo.append(undo_operation, redo_operation)

        if mark_unredo:
            self.unredo.mark()

    def set_col_width(self, col, tab, width, mark_unredo=True):
        """Sets column width"""

        if mark_unredo:
            self.unredo.mark()

        try:
            old_width = self.col_widths.pop((col, tab))

        except KeyError:
            old_width = None

        if width is not None:
            self.col_widths[(col, tab)] = float(width)

        # Make undoable

        undo_operation = (self.set_col_width,
                          [col, tab, old_width, mark_unredo])
        redo_operation = (self.set_col_width, [col, tab, width, mark_unredo])

        self.unredo.append(undo_operation, redo_operation)

        if mark_unredo:
            self.unredo.mark()

    # Element access via call

    __call__ = __getitem__

# End of class DataArray

# -----------------------------------------------------------------------------


class CodeArray(DataArray):
    """CodeArray provides objects when accessing cells via __getitem__

    Cell code can be accessed via function call

    This class represents layer 3 of the model.

    """

    # Cache for results from __getitem__ calls
    result_cache = {}

    # Cache for frozen objects
    frozen_cache = {}

    # Custom font storage
    custom_fonts = {}

    def __setitem__(self, key, value, mark_unredo=True):
        """Sets cell code and resets result cache"""

        # Prevent unchanged cells from being recalculated on cursor movement

        repr_key = repr(key)

        unchanged = (repr_key in self.result_cache and
                     value == self(key)) or \
                    ((value is None or value == "") and
                     repr_key not in self.result_cache)

        DataArray.__setitem__(self, key, value, mark_unredo=mark_unredo)

        if not unchanged:
            # Reset result cache
            self.result_cache = {}

    def __getitem__(self, key):
        """Returns _eval_cell"""

        # Frozen cell handling
        if all(type(k) is not slice for k in key):
            frozen_res = self.cell_attributes[key]["frozen"]
            if frozen_res:
                if repr(key) in self.frozen_cache:
                    return self.frozen_cache[repr(key)]
                else:
                    # Frozen cache is empty.
                    # Maybe we have a reload without the frozen cache
                    result = self._eval_cell(key, self(key))
                    self.frozen_cache[repr(key)] = result
                    return result

        # Normal cell handling

        if repr(key) in self.result_cache:
            return self.result_cache[repr(key)]

        elif self(key) is not None:
            result = self._eval_cell(key, self(key))
            self.result_cache[repr(key)] = result

            return result

    def _make_nested_list(self, gen):
        """Makes nested list from generator for creating numpy.array"""

        res = []

        for ele in gen:
            if ele is None:
                res.append(None)

            elif not isstring(ele) and isgenerator(ele):
                # Nested generator
                res.append(self._make_nested_list(ele))

            else:
                res.append(ele)

        return res

    def _get_updated_environment(self, env_dict=None):
        """Returns globals environment with 'magic' variable

        Parameters
        ----------
        env_dict: Dict, defaults to {'S': self}
        \tDict that maps global variable name to value

        """

        if env_dict is None:
            env_dict = {'S': self}

        env = globals().copy()
        env.update(env_dict)

        return env

    def exec_then_eval(self, code, _globals=None, _locals=None):
        """execs multuiline code and returns eval of last code line"""

        if _globals is None:
            _globals = {}

        if _locals is None:
            _locals = {}

        block = ast.parse(code, mode='exec')

        # assumes last node is an expression
        last_body = block.body.pop()
        last = ast.Expression(last_body.value)

        exec(compile(block, '<string>', mode='exec'), _globals, _locals)
        res = eval(compile(last, '<string>', mode='eval'), _globals, _locals)

        if hasattr(last_body, "targets"):
            for target in last_body.targets:
                print(target.id, type(res))
                _globals[target.id] = res

        globals().update(_globals)

        return res

    def _eval_cell(self, key, code):
        """Evaluates one cell and returns its result"""

        # Flatten helper function
        def nn(val):
            """Returns flat numpy array without None values"""
            try:
                return numpy.array([_f for _f in val.flat if _f])

            except AttributeError:
                # Probably no numpy array
                return numpy.array([_f for _f in val if _f])

        # Set up environment for evaluation

        env_dict = {'X': key[0], 'Y': key[1], 'Z': key[2], 'bz2': bz2,
                    'base64': base64, 'nn': nn, 'Figure': Figure,
                    'R': key[0], 'C': key[1], 'T': key[2], 'S': self}
        env = self._get_updated_environment(env_dict=env_dict)

        _old_code = self(key)

        # Return cell value if in safe mode

        if self.safe_mode:
            return code

        # If cell is not present return None

        if code is None:
            return

        elif isgenerator(code):
            # We have a generator object

            return numpy.array(self._make_nested_list(code), dtype="O")

        try:
            import signal

            signal.signal(signal.SIGALRM, self.handler)
            signal.alarm(self.settings.timeout)

        except Exception:
            # No POSIX system
            pass

        try:
            result = self.exec_then_eval(code, env, {})

        except AttributeError as err:
            # Attribute Error includes RunTimeError
            result = AttributeError(err)

        except RuntimeError as err:
            result = RuntimeError(err)

        except Exception as err:
            result = Exception(err)

        finally:
            try:
                signal.alarm(0)
            except Exception:
                # No POSIX system
                pass

        # Change back cell value for evaluation from other cells
        self.dict_grid[key] = _old_code

        return result

    def pop(self, key, mark_unredo=True):
        """Pops dict_grid with undo and redo support

        Parameters
        ----------
        key: 3-tuple of Integer
        \tCell key that shall be popped
        mark_unredo: Boolean, defaults to True
        \tIf True then an unredo marker is set after the operation

        """

        try:
            self.result_cache.pop(repr(key))

        except KeyError:
            pass

        return DataArray.pop(self, key, mark_unredo=mark_unredo)

    def reload_modules(self):
        """Reloads modules that are available in cells"""

        from importlib import reload
        modules = [bz2, base64, re, ast, sys, numpy, datetime]

        for module in modules:
            reload(module)

    def clear_globals(self):
        """Clears all newly assigned globals"""

        base_keys = ['cStringIO', 'KeyValueStore', 'UnRedo',
                     'isgenerator', 'isstring', 'bz2', 'base64',
                     '__package__', 're', '__doc__', 'QPixmap',
                     'CellAttributes', 'product', 'ast', '__builtins__',
                     '__file__', 'sys', 'isslice', '__name__', 'QImage',
                     'copy', 'imap', 'ifilter', 'Selection', 'DictGrid',
                     'numpy', 'CodeArray', 'DataArray', 'datetime']

        for key in list(globals().keys()):
            if key not in base_keys:
                globals().pop(key)

    def get_globals(self):
        """Returns globals dict"""

        return globals()

    def execute_macros(self):
        """Executes all macros and returns result string

        Executes macros only when not in safe_mode

        """

        if self.safe_mode:
            return '', "Safe mode activated. Code not executed."

        # Windows exec does not like Windows newline
        self.macros = self.macros.replace('\r\n', '\n')

        # Set up environment for evaluation
        globals().update(self._get_updated_environment())

        # Create file-like string to capture output
        import io
        code_out = io.StringIO()
        code_err = io.StringIO()
        err_msg = io.StringIO()

        # Capture output and errors
        sys.stdout = code_out
        sys.stderr = code_err

        try:
            import signal

            signal.signal(signal.SIGALRM, self.handler)
            signal.alarm(self.settings.timeout)

        except Exception:
            # No POSIX system
            pass

        try:
            exec(self.macros, globals())
            try:
                signal.alarm(0)
            except Exception:
                # No POSIX system
                pass

        except Exception:
            # Print exception
            # (Because of how the globals are handled during execution
            # we must import modules here)
            from traceback import print_exception
            from src.lib.exception_handling import get_user_codeframe
            exc_info = sys.exc_info()
            user_tb = get_user_codeframe(exc_info[2]) or exc_info[2]
            print_exception(exc_info[0], exc_info[1], user_tb, None, err_msg)
        # Restore stdout and stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        results = code_out.getvalue()
        errs = code_err.getvalue() + err_msg.getvalue()

        code_out.close()
        code_err.close()

        # Reset result cache
        self.result_cache.clear()

        # Reset frozen cache
        self.frozen_cache.clear()

        return results, errs

    def _sorted_keys(self, keys, startkey, reverse=False):
        """Generator that yields sorted keys starting with startkey

        Parameters
        ----------

        keys: Iterable of tuple/list
        \tKey sequence that is sorted
        startkey: Tuple/list
        \tFirst key to be yielded
        reverse: Bool
        \tSort direction reversed if True

        """

        def tuple_key(t):
            return t[::-1]

        if reverse:
            def tuple_cmp(t):
                return t[::-1] > startkey[::-1]
        else:
            def tuple_cmp(t):
                return t[::-1] < startkey[::-1]

        searchkeys = sorted(keys, key=tuple_key, reverse=reverse)
        searchpos = sum(1 for _ in filter(tuple_cmp, searchkeys))

        searchkeys = searchkeys[searchpos:] + searchkeys[:searchpos]

        for key in searchkeys:
            yield key

    def string_match(self, datastring, findstring, flags=None):
        """
        Returns position of findstring in datastring or None if not found.

        :param datastring:
        :param findstring:
        :param flags: is a list of strings

        Supported flag strings are:
         * MATCH_CASE: The case has to match for valid find
         * WHOLE_WORD: The word has to be surrounded by whitespace
           characters if in the middle of the string
         * REG_EXP:    A regular expression is evaluated.

        """

        if type(datastring) is int:  # Empty cell
            return None

        if flags is None:
            flags = []

        if "REG_EXP" in flags:
            match = re.search(findstring, datastring)
            if match is None:
                pos = -1
            else:
                pos = match.start()
        else:
            if "MATCH_CASE" not in flags:
                datastring = datastring.lower()
                findstring = findstring.lower()

            if "WHOLE_WORD" in flags:
                pos = -1
                matchstring = r'\b' + findstring + r'+\b'
                for match in re.finditer(matchstring, datastring):
                    pos = match.start()
                    break  # find 1st occurrance
            else:
                pos = datastring.find(findstring)

        if pos == -1:
            return None
        return pos

    def findnextmatch(self, startkey, find_string, flags, search_result=True):
        """ Returns a tuple with the position of the next match of find_string

        Returns None if string not found.

        Parameters:
        -----------
        startkey:   Start position of search
        find_string:String to be searched for
        flags:      List of strings, out of
                    ["UP" xor "DOWN", "WHOLE_WORD", "MATCH_CASE", "REG_EXP"]
        search_result: Bool, defaults to True
        \tIf True then the search includes the result string (slower)

        """

        assert "UP" in flags or "DOWN" in flags
        assert not ("UP" in flags and "DOWN" in flags)

        if search_result:
            def is_matching(key, find_string, flags):
                code = self(key)
                if self.string_match(code, find_string, flags) is not None:
                    return True
                else:
                    res_str = str(self[key])
                    return self.string_match(res_str, find_string, flags) \
                        is not None

        else:
            def is_matching(code, find_string, flags):
                code = self(key)
                return self.string_match(code, find_string, flags) is not None

        # List of keys in sgrid in search order

        reverse = "UP" in flags

        for key in self._sorted_keys(list(self.keys()), startkey,
                                     reverse=reverse):
            try:
                if is_matching(key, find_string, flags):
                    return key

            except Exception:
                # re errors are cryptical: sre_constants,...
                pass

    def handler(self, signum, frame):
        raise RuntimeError("Timeout after {} s.".format(self.settings.timeout))

# End of class CodeArray
