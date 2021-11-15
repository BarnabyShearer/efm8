efm8
====

Flash via AN945: EFM8 Factory Bootloader HID.

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


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   install
   efm8
   efm8_read
   u2fzero

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
