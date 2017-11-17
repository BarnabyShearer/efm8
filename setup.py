""""""
from setuptools import setup
from os import path

with open(path.join(path.abspath(path.dirname(__file__)), 'README.rst')) as f:
    long_description = f.read()

setup(
    name="efm8",
    version="0.0.1",
    description="Flash via AN945: EFM8 Factory Bootloader HID",
    long_description=long_description,
    author="Barnaby Shearer",
    author_email="b@Zi.iS",
    url="https://github.com/BarnabyShearer/efm8.git",
    license='BSD',
    keywords="EFM8 AN945 HID Bootloader",
    scripts=[
        "efm8.py",
        "u2fzero.py"
    ],
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
