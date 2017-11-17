EFM8
====

Flash via AN945: EFM8 Factory Bootloader HID

::

    sudo apt install libusb-1.0-0-dev libudev-dev python-dev
    pip install efm8
    efm8.py firmware.hex

Also includes an example that resets a https://u2fzero.com/ into the bootloader and flashes in one command.

::

    u2fzero.py firmware.hex
