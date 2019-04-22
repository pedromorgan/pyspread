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

hashing
=======

File hashing services

Provides
--------

 * genkey: Generates hash key
 * sign: Returns a signature for a given file
 * verify: Verifies file against signature

"""

from hashlib import blake2b
from hmac import compare_digest
import secrets

from settings import Settings


def genkey(nbytes=64):
    """Returns a new signature key of nbytes

    64 bytes is recommended for BLAKE2b

    """

    return secrets.token_bytes(nbytes)


def sign(data, key=None):
    """Returns signature for file

    If key is None use settings key.

    """

    if key is None:
        settings = Settings()
        key = settings.signature_key

    if not key:
        raise ValueError("No signature key defined")

    signature = blake2b(digest_size=64, key=key)
    signature.update(data)

    return signature.hexdigest().encode('utf-8')


def verify(data, signature, key=None):
    """Verifies a signature, returns True if successful else False

    If key is None use settings key.

    """

    if key is None:
        settings = Settings()
        key = settings.signature_key

    data_signature = sign(data, key)
    return compare_digest(data_signature, signature)
