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
"""Extra utils for U2F-Zero devices."""

from __future__ import print_function

import argparse
import contextlib
import fcntl
import os
import time
from typing import Union  # noqa: F401

import hid  # type: ignore

import efm8

U2F_CONFIG_BOOTLOADER = 0x88
USBDEVFS_RESET = ord("U") << (4 * 2) | 20


def reset(manufacturer, product, serial):
    # Type: (int, int, Union[str, bytes]) -> None
    """Send zeroU2F jump to bootloader, trigger the host to see the device change."""
    with contextlib.closing(hid.device()) as dev:
        if hasattr(serial, "decode"):  # pragma: no cover
            serial = serial.decode("ascii")  # type: ignore
        dev.open(manufacturer, product, serial)
        print("Jumping to bootloader (LED should go out)")
        dev.write([0, U2F_CONFIG_BOOTLOADER])
        dev.write([0, 0xFF, 0xFF, 0xFF, 0xFF, U2F_CONFIG_BOOTLOADER])
    # Force host to detect the changed device
    for dev in hid.enumerate(manufacturer, product):  # pragma: no cover
        path = dev["path"]
        if hasattr(path, "decode"):
            path = path.decode("ascii")
        path = path.split(":")
        path = "/dev/bus/usb/%03d/%03d" % (int(path[0], 16), int(path[1], 16))
        print("Resetting", path)
        fsdev_fd = os.open(path, os.O_WRONLY)
        try:
            fcntl.ioctl(fsdev_fd, USBDEVFS_RESET, 0)
        except IOError:  # always returns "No such device" even if it has worked
            pass
        finally:
            os.close(fsdev_fd)
        time.sleep(1)


def _parser():
    # Type: () -> argparse.ArgumentParser
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-p", "--product", help="USB Product ID of device to program", default="EAC9"
    )
    parser.add_argument("-s", "--serial", help="Serial number of device to program")
    parser.add_argument("firmware", help="Intel Hex format file to flash")
    return parser


def main():  # pragma: no cover
    # Type: () -> None
    """Command line."""
    args = _parser().parse_args()

    try:
        reset(0x10C4, 0x8ACF, args.serial)
    except IOError:  # maybe we already were in bootloader
        pass
    efm8.flash(
        0x10C4,
        int(args.product, 16),
        args.serial,
        efm8.to_frames(efm8.read_intel_hex(args.firmware)),
    )


if __name__ == "__main__":  # pragma: no cover
    main()
