====
efm8
====
.. image:: https://readthedocs.org/projects/efm8/badge/?version=latest
    :target: https://efm8.readthedocs.io/en/latest/?badge=latest

.. image:: https://badge.fury.io/py/efm8.svg
    :target: https://badge.fury.io/py/efm8

Flash via AN945: EFM8 Factory Bootloader HID.

Install
-------

::

    sudo apt install libusb-1.0-0-dev libudev-dev
    python3 -m pip install efm8

Usage
-----

Communication is over USB-HID. This is implemented via the `hidapi <https://github.com/trezor/cython-hidapi>`__ pthon wrapper for the `hidapi <https://github.com/signal11/hidapi>`__ native library.

On linux you can use udev to grant access:

::

    echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="10c4", MODE="0666"' | sudo tee /etc/udev/rules.d/70-silabs.rules
    udevadm trigger

::

    efm8 firmware.hex

Also includes an example that resets a https://u2fzero.com/ into the bootloader and flashes in one command.

::

    u2fzero firmware.hex

And a way to (slowly) read the firmware back

::

    efm8_read firmware.hex

