#!/usr/bin/env python3
"""Sphinx config."""

import os
import sys
from unittest.mock import Mock

sys.modules["hid"] = Mock()
sys.modules["PyCRC.CRCCCITT"] = Mock()
sys.path.insert(0, os.path.abspath(".."))

extensions = ["sphinxcontrib.autoprogram", "sphinx.ext.autodoc"]

project = "EFM8 Bootloader"
copyright = "2017, Barnaby Shearer"
author = "Barnaby Shearer"

version = "0.0"
release = "0.0.2"

master_doc = "index"
