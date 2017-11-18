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

"""
Read flash via AN945: EFM8 Factory Bootloader HID

Note the is no read command, instead we naively brute-force the VERIFY checksum; takes about 12min
"""

from __future__ import print_function, division
import sys
import contextlib
import argparse
import efm8
import hid

SIZE = 0x4000 #16Kb

def read_flash(manufacturer, product, serial):
    """Exploit CRC to read back firmware"""
    #pylint: disable-msg=no-member
    with contextlib.closing(hid.device()) as dev:
        if hasattr(serial, "decode"):
            serial = serial.decode("ascii")
        dev.open(manufacturer, product, serial)
        dev.send_feature_report([0] + efm8.create_frame(efm8.SETUP, [0xa5, 0xf1, 0x00]))
        buf = []
        for addr in range(SIZE):
            if addr % 128 == 0:
                print("%fkB" % (addr / 0x400))
                sys.stdout.flush()
            for test in range(0x100):
                dev.send_feature_report([0] + efm8.create_frame(
                    efm8.VERIFY,
                    efm8.toaddr(addr) + efm8.toaddr(addr) + efm8.crc([test])
                ))
                if dev.get_feature_report(0, 2)[-1] == 64:
                    buf.append(test)
                    break
                if test == 0xFF:
                    raise efm8.BadResponse("No posible CRC matches")
    return buf

def write_hex(buf, filename):
    """Write an Intel Format Hex file"""
    with open(filename, "w") as output:
        output.write(":020000040000FA\n")
        for addr in range(0, SIZE, 16):
            output.write(":10{:04X}00".format(addr))
            output.write("".join("{:02X}".format(c) for c in buf[addr:addr + 16]))
            output.write(
                "{:02X}\n".format(
                    efm8.twos_complement(
                        sum([0x10] + efm8.toaddr(addr) + buf[addr:addr + 16]) & 0xFF
                    )
                )
            )
        output.write(":00000001FF\n")

def main():
    """Command line"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-s", "--serial", help="Serial number of device to program")
    parser.add_argument("firmware", help="Intel Hex format file to flash")
    args = parser.parse_args()
    write_hex(
        read_flash(
            0x10C4,
            0xEAC9,
            args.serial
        ),
        args.firmware
    )


if __name__ == "__main__":
    main()
