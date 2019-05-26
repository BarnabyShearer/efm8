""""""
from setuptools import setup
from os import path

with open(path.join(path.abspath(path.dirname(__file__)), 'README.rst')) as f:
    long_description = f.read()

setup(
    name="efm8",
    version="0.0.3",
    description="Flash via AN945: EFM8 Factory Bootloader HID",
    long_description=long_description,
    author="Barnaby Shearer",
    author_email="b@Zi.iS",
    url="https://github.com/BarnabyShearer/efm8.git",
    license='BSD',
    keywords="EFM8 AN945 HID Bootloader",
    packages=[
        "efm8"
    ],
    entry_points={
        "console_scripts": [
            "efm8 = efm8.__main__:main",
            "efm8_read = efm8.__main__:read",
            "u2fzero = efm8.u2fzero:main",
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3"
    ],
    install_requires=[
        'hidapi>=0.7.99.post21',
        'PyCRC>=1.21'
    ]
)
