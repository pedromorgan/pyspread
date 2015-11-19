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
grid_panels.py
==============

Panels that can be used from within a grid cell.

The panels pop up if they are a cell result. They stay in front of the cell.
This allows dynamic and interactive cell content.

Provides
--------

 * BaseGridPanel: Basic panel that provides UI functionality for useage in grid

 * VLCPanel: Video panel that uses the VLC player

"""

import wx

import src.lib.i18n as i18n

try:
    import src.lib.vlc as vlc

except ImportError:
    vlc = None

_ = i18n.language.ugettext


class BaseGridPanel(wx.Panel):
    """Basic panel that provides UI functionality for useage in grid"""

    pass


class VLCPanel(BaseGridPanel):
    """Basic panel that provides UI functionality for useage in grid"""

    def __init__(self, *args, **kwargs):
        BaseGridPanel.__init__(self, *args, **kwargs)

        filepath = "/home/mn/tmp/pyspread_video/pyspread_podcast_1.mp4"

        self.SetBackgroundColour(wx.BLACK)

        # VLC player controls
        self.Instance = vlc.Instance()
        self.player = self.Instance.media_player_new()
        self.Media = self.Instance.media_new(filepath)
        self.player.set_media(self.Media)
        self.player.set_xwindow(self.GetHandle())
        self.player.play()

    def adjust_video_panel(self, grid, rect):
        """Positions and resizes video panel

        Parameters
        ----------
        rect: 4-tuple of Integer
        \tRect area of video panel

        """

        panel_posx = rect[0] + grid.GetRowLabelSize()
        panel_posy = rect[1] + grid.GetColLabelSize()

        panel_scrolled_pos = grid.CalcScrolledPosition(panel_posx, panel_posy)

        self.SetPosition(panel_scrolled_pos)
        self.SetClientRect(wx.Rect(*rect))
