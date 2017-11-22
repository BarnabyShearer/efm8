Installation
============

Communication is over USB-HID. This is implemented via the `hidapi <https://github.com/trezor/cython-hidapi>`__ pthon wrapper for the `hidapi <https://github.com/signal11/hidapi>`__ native library.

On linux you can use udev to grant access:

::

    echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="10c4", MODE="0666"' | sudo tee /etc/udev/rules.d/70-silabs.rules
    udevadm trigger

Then install some native prerequisites:

::

    sudo apt install libusb-1.0-0-dev libudev-dev python-dev

Then `pip` install:

::

    pip install efm8

