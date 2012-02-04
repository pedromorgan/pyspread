#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2011 Martin Manns
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

gpg
===

GPG handling functions

Provides
--------

 * is_pyme_present: Checks if pyme is installed
 * genkey: Generates gpg key
 * sign: Returns detached signature for file
 * verify: verifies stream against signature

"""

import wx
import wx.lib.agw.genericmessagedialog as GMD

from src.config import config


from pyme import core, pygpgme
import pyme.errors


def _passphrase_callback(hint='', desc='', prev_bad=''):
    """Callback function needed by pyme"""

    return config["gpg_key_passphrase"]


def _get_file_data(filename):
    """Returns pyme.core.Data object of file."""

    # Required because of unicode bug in pyme

    infile = open(filename, "rb")
    infile_content = infile.read()
    infile.close()

    return core.Data(string=infile_content)


def choose_uid(context):
    """Displays gpg key choice and returns uid name or None on Cancel"""

    gpg_uids = []
    uid_strings = []

    for key in context.op_keylist_all("", 0):
        if key.can_sign and key.owner_trust and not key.invalid:
            for uid in key.uids:
                uid_data = uid.uid, uid.name, uid.email, uid.comment
                gpg_uids.append(uid.name)
                uid_strings.append("\t".join(uid_data))

    dlg = wx.SingleChoiceDialog(
            None,
            'Choose a GPG key that you own for signing pyspread save files.\n'
            'Pressing Cancel creates a new key.',
            'Choose key',
            uid_strings, wx.CHOICEDLG_STYLE,
            )

    if dlg.ShowModal() == wx.ID_OK:
        uid = gpg_uids[uid_strings.index(dlg.GetStringSelection())]

    else:
        uid = None

    dlg.Destroy()

    return uid


def get_key_params_string(params):
    """Returns parameter string from given params dict"""

    param_head = '<GnupgKeyParms format="internal">'
    param_foot = '</GnupgKeyParms>'

    param_str_list = [param_head, param_foot]

    for param in params[::-1]:
        param_str_list.insert(1, ": ".join(param))

    return str("\n".join(param_str_list))


class GPGParamsDialog(wx.Dialog):
    """Gets GPG key paarmeters from user"""

    def __init__(self, parent, ID, title, params):
        wx.Dialog.__init__(self, parent, ID, title)

        sizer = wx.FlexGridSizer(len(params), 2, 5, 5)

        label = wx.StaticText(self, -1, "GPG key data")
        sizer.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        sizer.Add(wx.Panel(self, -1), 0, wx.ALIGN_CENTRE | wx.ALL, 5)

        self.textctrls = []

        for labeltext, _, pwd in params:
            label = wx.StaticText(self, -1, labeltext)
            sizer.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

            if pwd:
                textctrl = wx.TextCtrl(self, -1, "", size=(80, -1),
                                       style=wx.TE_PASSWORD)
            else:
                textctrl = wx.TextCtrl(self, -1, "", size=(80, -1))

            self.textctrls.append(textctrl)

            sizer.Add(textctrl, 1, wx.ALIGN_CENTRE | wx.ALL, 5)

        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        sizer.Add(btn)

        self.SetSizer(sizer)
        sizer.Fit(self)


def get_key_params_from_user():
    """Displays parameter entry dialog and returns parameter string"""

    gpg_key_parameters = [ \
        ('Key-Type', 'DSA'),
        ('Key-Length', '2048'),
        ('Subkey-Type', 'ELG-E'),
        ('Subkey-Length', '2048'),
        ('Expire-Date', '0'),
    ]

    PASSWD = True
    NO_PASSWD = False

    params = [ \
        ['Real name', 'Name-Real', NO_PASSWD],
        ['Passphrase', 'Passphrase', PASSWD],
        ['E-mail', 'Name-Email', NO_PASSWD],
        ['Real name', 'Name-Comment', NO_PASSWD],
    ]

    vals = [""]

    while "" in vals:
        dlg = GPGParamsDialog(None, -1, "Enter GPG key parameters", params)
        dlg.CenterOnScreen()

        dlg.ShowModal()
        vals = [textctrl.Value for textctrl in dlg.textctrls]
        dlg.Destroy()

        if "" in vals:
            msg = "Please enter a value in each field."

            dlg = GMD.GenericMessageDialog(None, msg, "Missing value",
                                           wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

    for (_, key, _), val in zip(params, vals):
        gpg_key_parameters.insert(-2, (key, val))

    print gpg_key_parameters

    return get_key_params_string(gpg_key_parameters)


def genkey():
    """Creates a new standard GPG key"""

    # Initialize our context.
    core.check_version(None)

    context = core.Context()
    context.set_armor(1)

    # Check if standard key is already present
    keyname = config["gpg_key_uid"]
    context.op_keylist_start(keyname, 0)
    key = context.op_keylist_next()

    # If no key is chosen generate one

    if key is None:
        # If no GPG key is set in config, choose one

        uid = choose_uid(context)
        config["gpg_key_uid"] = repr(uid)

    if key is None:

        # Key not present --> Create new one

        # Show progress dialog

        dlg = wx.ProgressDialog("GPG key generation",
                               "Generating new GPG key " + keyname + \
                               ".\nThis may take some time.\n \n" + \
                               "Progress bar may stall. Please wait.",
                               maximum=200,
                               parent=None,
                               style=wx.PD_ELAPSED_TIME)

        class CBFs(object):
            """Callback functions for pyme"""

            progress = 0

            def cbf(self, what=None, type=None, current=None, total=None,
                    hook=None):
                """Callback function that updates progress dialog"""

                dlg.Update(self.progress % 199)
                self.progress += 1

        cbfs = CBFs()

        gpg_key_parameters = get_key_params_from_user()

        print gpg_key_parameters

        context.set_progress_cb(cbfs.cbf, None)

        context.op_genkey(gpg_key_parameters, None, None)

        dlg.Destroy()


def sign(filename):
    """Returns detached signature for file"""

    plaintext = _get_file_data(filename)

    ciphertext = core.Data()

    ctx = core.Context()

    ctx.set_armor(1)
    ctx.set_passphrase_cb(_passphrase_callback)

    ctx.op_keylist_start(config["gpg_key_uid"], 0)
    sigkey = ctx.op_keylist_next()
    ##print sigkey.uids[0].uid

    ctx.signers_clear()
    ctx.signers_add(sigkey)

    ctx.op_sign(plaintext, ciphertext, pygpgme.GPGME_SIG_MODE_DETACH)

    ciphertext.seek(0, 0)
    signature = ciphertext.read()

    return signature


def verify(sigfilename, filefilename=None):
    """Verifies a signature, returns True if successful else False."""

    context = core.Context()

    # Create Data with signed text.
    __signature = _get_file_data(sigfilename)

    if filefilename:
        __file = _get_file_data(filefilename)
        __plain = None
    else:
        __file = None
        __plain = core.Data()

    # Verify.
    try:
        context.op_verify(__signature, __file, __plain)
    except pyme.errors.GPGMEError:
        return False

    result = context.op_verify_result()

    # List results for all signatures. Status equal 0 means "Ok".
    validation_sucess = False

    for signature in result.signatures:
        if (not signature.status) and signature.validity:
            validation_sucess = True

    return validation_sucess