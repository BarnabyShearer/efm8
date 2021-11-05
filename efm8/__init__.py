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

import contextlib
import sys
from typing import List, Union  # noqa: F401

import hid  # type: ignore
from PyCRC.CRCCCITT import CRCCCITT  # type: ignore

SETUP = 0x31
ERASE = 0x32
WRITE = 0x33
VERIFY = 0x34
RUN = 0x36


class Unsupported(IOError):
    """Input file not understood."""


class BadChecksum(IOError):
    """Checksum mismatch."""


class BadResponse(IOError):
    """Command not confirmed."""


def twos_complement(input_value, num_bits=8):
    # Type: (int, int) -> int
    """Calculate unsigned int which binary matches the two's complement of the input."""
    mask = 2 ** (num_bits - 1)
    return ((input_value & mask) - (input_value & ~mask)) & ((2 ** num_bits) - 1)


def toaddr(addr):
    # Type: (int) -> List[int]
    """Split a 16bit address into two bytes (dosn't check it is a 16bit address ;-)."""
    return [addr >> 8, addr & 0xFF]


def crc(data):
    # Type: (List[int]) -> List[int]
    """CITT-16, XModem."""
    buf = "".join(map(chr, data)) if sys.version_info < (3, 0) else bytes(data)
    ret = CRCCCITT().calculate(buf)
    return [ret >> 8, ret & 0xFF]


def create_frame(cmd, data):
    # Type: (int, List[int]) -> List[int]
    """Bootloader frames start with '$', 1 byte length, 1 byte command, x bytes data."""
    return [ord("$"), 1 + len(data), cmd] + data


def read_intel_hex(filename):
    # Type: (str) -> List[int]
    """Read simple Intel format Hex files into byte array."""
    data = []
    address = 0
    with open(filename) as hexfile:
        for line in hexfile.readlines():
            if line[0] != ":":
                continue
            if line.startswith(
                ":020000040000FA"
            ):  # Confirms default Extended linear Address
                continue
            if line.startswith(":00000001FF"):  # EOF
                break
            if line[7:9] != "00":
                raise Unsupported("We only cope with very simple HEX files")
            if int(line[3:7], 16) < address:
                raise Unsupported("We conly cope with liner HEX files")
            # Zero pad gaps
            data += [0] * (int(line[3:7], 16) - address)
            address = int(line[3:7], 16)
            length = 9 + int(line[1:3], 16) * 2  # input chars
            if int(line[length : length + 2], 16) != twos_complement(
                sum([int(line[x : x + 2], 16) for x in range(1, length, 2)]) & 0xFF
            ):
                raise BadChecksum()
            address += int(line[1:3], 16)
            data += [int(line[x : x + 2], 16) for x in range(9, length, 2)]
    if data == []:
        raise Unsupported("No Intel HEX lines found")
    return data


def to_frames(data, checksum=True, run=True):
    # Type: (List[int], bool, bool) -> List[List[int]]
    """Convert firmware byte array into sequence of bootloader frames."""
    data_zero = data[0]
    data[0] = 0xFF  # Ensure we don't boot a half-written firmware

    frames = [create_frame(SETUP, [0xA5, 0xF1, 0x00])]
    for addr in range(0, len(data), 128):
        frames.append(
            create_frame(
                ERASE if addr % 0x200 == 0 else WRITE,
                toaddr(addr) + data[addr : addr + 128],
            )
        )
    if checksum:
        frames.append(create_frame(VERIFY, [0, 0] + toaddr(len(data) - 1) + crc(data)))
    frames.append(create_frame(WRITE, [0, 0, data_zero]))
    if run:
        frames.append(create_frame(RUN, [0, 0]))
    return frames


def flash(manufacturer, product, serial, frames):
    # Type: (int, int, Union[str, bytes], List[List[int]]) -> None
    """Send bootloader frames over HID, and check confirmations."""
    with contextlib.closing(hid.device()) as dev:
        if hasattr(serial, "decode"):  # pragma: no cover
            serial = serial.decode("ascii")  # type: ignore
        dev.open(manufacturer, product, serial)
        print("Download over port: HID:%X:%X" % (manufacturer, product))
        print()
        for frame in frames:
            print("$", " ".join("{:02X}".format(c) for c in frame[1:9]), end=" > ")
            for off in range(0, len(frame), 64):
                dev.send_feature_report([0] + frame[off : off + 64])
            report = dev.get_feature_report(0, 2)
            print(chr(report[-1]))
            if report[-1] != 64:
                if frame[2] == VERIFY:
                    raise BadChecksum()
                raise BadResponse()


def read_flash(manufacturer, product, serial, length):
    # Type: (int, int, Union[str, bytes], int) -> List[int]
    """Exploit CRC to read back firmware."""
    with contextlib.closing(hid.device()) as dev:
        if hasattr(serial, "decode"):  # pragma: no cover
            serial = serial.decode("ascii")  # type: ignore
        dev.open(manufacturer, product, serial)
        dev.send_feature_report([0] + create_frame(SETUP, [0xA5, 0xF1, 0x00]))
        buf = []
        for addr in range(length):
            if addr % 128 == 0:
                print("%fkB" % (addr / 0x400))
                sys.stdout.flush()
            for test in range(0x100):  # pragma: no branch
                dev.send_feature_report(
                    [0]
                    + create_frame(VERIFY, toaddr(addr) + toaddr(addr) + crc([test]))
                )
                if dev.get_feature_report(0, 2)[-1] == 64:
                    buf.append(test)
                    break
                if test == 0xFF:
                    raise BadResponse("No posible CRC matches")
    return buf


def write_hex(buf, filename):
    # Type: (List[int], str) -> None
    """Write an Intel Format Hex file."""
    with open(filename, "w") as output:
        output.write(":020000040000FA\n")
        for addr in range(0, len(buf), 16):
            output.write(":10{:04X}00".format(addr))
            output.write("".join("{:02X}".format(c) for c in buf[addr : addr + 16]))
            output.write(
                "{:02X}\n".format(
                    twos_complement(
                        sum([0x10] + toaddr(addr) + buf[addr : addr + 16]) & 0xFF
                    )
                )
            )
        output.write(":00000001FF\n")
