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

import sys

import wx
import wx.lib.agw.genericmessagedialog as GMD
import gnupg

import src.lib.i18n as i18n
from src.config import config
from src.gui._gui_interfaces import get_key_params_from_user

from pyme import core, pygpgme, errors
import pyme.errors

#use ugettext instead of getttext to avoid unicode errors
_ = i18n.language.ugettext


def _passphrase_callback(hint='', desc='', prev_bad=''):
    """Callback function needed by pyme"""

    return str(config["gpg_key_passphrase"])


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
          _('Choose a GPG key that you own for signing pyspread save files.\n'
            'Pressing Cancel creates a new key.'),
          _('Choose key'),
            uid_strings, wx.CHOICEDLG_STYLE,
            )

    sizer = dlg.GetSizer()
    store_passwd_checkbox = wx.CheckBox(dlg, True, _("   Store passphrase"),
                                        style=wx.ALIGN_RIGHT)
    store_passwd_checkbox.SetValue(True)

    sizer.Insert(1, store_passwd_checkbox)

    dlg.SetBestFittingSize()

    if dlg.ShowModal() == wx.ID_OK:
        uid = gpg_uids[uid_strings.index(dlg.GetStringSelection())]
        config["gpg_key_passphrase_isstored"] = \
            repr(store_passwd_checkbox.Value)

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


def choose_uid_key(keylist):
    """Displays gpg key choice and returns uid and key dict"""

    uid_strings = []
    uid_string2key = {}

    for key in keylist:
        for uid_string in key['uids']:
            uid_strings.append(uid_string)
            uid_string2key[uid_string] = key

    dlg = wx.SingleChoiceDialog(
            None,
          _('Choose a GPG key that you own for signing pyspread save files.\n'
            'Pressing Cancel creates a new key.'),
          _('Choose key'),
            uid_strings, wx.CHOICEDLG_STYLE,
            )

    dlg.SetBestFittingSize()

    if dlg.ShowModal() == wx.ID_OK:
        uid = dlg.GetStringSelection()
        key = uid_string2key[uid]

    else:
        uid = None
        key = None

    dlg.Destroy()

    return uid, key


def genkey():
    """Creates a new standard GPG key"""

    gpg = gnupg.GPG()

    gpg.encoding = 'utf-8'

    # Check if standard key is already present

    pyspread_key_uid = str(config["gpg_key_uid"])
    gpg_private_keylist = gpg.list_keys(True)

    pyspread_key = None

    for private_key in gpg_private_keylist:
        if pyspread_key_uid in private_key["uids"]:
            pyspread_key = private_key

    if pyspread_key is None:
        # If no GPG key is set in config, choose one
        pyspread_key_uid, pyspread_key = choose_uid_key(gpg_private_keylist)

    if pyspread_key:
        # A key has been chosen
        config["gpg_key_uid"] = repr(pyspread_key_uid)

    else:
        # No key has been chosen --> Create new one
        gpg_key_parameters = get_key_params_from_user()

        input_data = gpg.gen_key_input(**gpg_key_parameters)

        # Generate key
        # ------------

        # Show infor dialog

        style = wx.ICON_INFORMATION | wx.DIALOG_NO_PARENT | wx.OK | wx.CANCEL
        pyspread_key_uid = gpg_key_parameters["name_real"]
        short_message = _("New GPG key").format(pyspread_key_uid)
        message = _("After confirming this dialog, a new GPG key ") + \
                  _("'{}' will be generated.").format(pyspread_key_uid) + \
                  _(" \n \nThis may take some time.\nPlease wait.\n \n") + \
                  _("Canceling this operation exits pyspread.")
        dlg = GMD.GenericMessageDialog(None, message, short_message, style)
        dlg.Centre()

        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()
            fingerprint = gpg.gen_key(input_data)

            for private_key in gpg.list_keys(True):
                if str(fingerprint) == private_key['fingerprint']:
                    config["gpg_key_uid"] = repr(private_key['uids'][0])

        else:
            dlg.Destroy()
            sys.exit()


def sign(filename):
    """Returns detached signature for file"""

    plaintext = _get_file_data(filename)

    ciphertext = core.Data()

    ctx = core.Context()

    ctx.set_armor(1)
    ctx.set_passphrase_cb(_passphrase_callback)

    ctx.op_keylist_start(str(config["gpg_key_uid"]), 0)
    sigkey = ctx.op_keylist_next()
    ##print sigkey.uids[0].uid

    ctx.signers_clear()
    ctx.signers_add(sigkey)

    passwd_is_incorrect = None

    while passwd_is_incorrect is None or passwd_is_incorrect:
        try:
            ctx.op_sign(plaintext, ciphertext, pygpgme.GPGME_SIG_MODE_DETACH)
            passwd_is_incorrect = False

        except errors.GPGMEError:
            passwd_is_incorrect = True

            uid = config["gpg_key_uid"]
            stored = config["gpg_key_passphrase_isstored"]

            passwd = get_gpg_passwd_from_user(stored, passwd_is_incorrect, uid)

            if passwd is None:
                return

            config["gpg_key_passphrase"] = repr(passwd)
            ctx.set_passphrase_cb(_passphrase_callback)

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