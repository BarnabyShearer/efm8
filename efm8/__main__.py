#!/usr/bin/env python
#
# Copyright (c) 2017, Barnaby <b@zi.is>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Flash via AN945: EFM8 Factory Bootloader HID."""

from __future__ import print_function

import argparse

import efm8


def _parser(read=False):
    # Type: (bool) -> argparse.ArgumentParser
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-p", "--product", help="USB Product ID of device to program", default="EAC9"
    )
    parser.add_argument("-s", "--serial", help="Serial number of device to program")
    parser.add_argument("firmware", help="Intel Hex format file to flash")
    if read:
        parser.add_argument("-l", "--length", help="Length to read", default="0x4000")
    return parser


def main():  # pragma: no cover
    # Type: () -> None
    """Command line."""
    args = _parser().parse_args()
    efm8.flash(
        0x10C4,
        int(args.product, 16),
        args.serial,
        efm8.to_frames(efm8.read_intel_hex(args.firmware)),
    )


def read():  # pragma: no cover
    # Type: () -> None
    """Command line."""
    parser = _parser(True)
    args = parser.parse_args()
    efm8.write_hex(
        efm8.read_flash(
            0x10C4, int(args.product, 16), args.serial, int(args.length, 16)
        ),
        args.firmware,
    )


if __name__ == "__main__":  # pragma: no cover
    main()
