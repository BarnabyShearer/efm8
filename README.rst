====
efm8
====
.. image:: https://readthedocs.org/projects/efm8/badge/?version=latest
    :target: https://efm8.readthedocs.io/en/latest/?badge=latest

.. image:: https://badge.fury.io/py/efm8.svg
    :target: https://badge.fury.io/py/efm8

Flash via AN945: EFM8 Factory Bootloader HID.

::

    sudo apt install libusb-1.0-0-dev libudev-dev python-dev
    pip install efm8
    efm8 firmware.hex

Also includes an example that resets a https://u2fzero.com/ into the bootloader and flashes in one command.

::

    u2fzero firmware.hex

And a way to (slowly) read the firmware back

::

    efm8_read firmware.hex



