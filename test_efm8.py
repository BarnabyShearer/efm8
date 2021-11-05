"""Test file parsing and framing (but not hardware communication)."""

import sys

try:
    from unittest.mock import mock_open, patch
except ImportError:  # pragma: no cover
    from mock import patch, mock_open

import pytest

import efm8
import efm8.__main__ as efm8_main
import efm8.u2fzero


def test_twos():
    """Test exepcted outputs."""
    assert efm8.twos_complement(0xE2) == 0x1E
    assert efm8.twos_complement(0xFF) == 0x01
    assert efm8.twos_complement(0x00) == 0x00
    assert efm8.twos_complement(0x80) == 0x80


def test_toaddr():
    """Test exepcted outputs."""
    assert efm8.toaddr(0xFFFF) == [0xFF, 0xFF]
    assert efm8.toaddr(0x0102) == [0x01, 0x02]
    assert efm8.toaddr(0x0000) == [0x00, 0x00]


def test_crc():
    """Test exepcted outputs."""
    assert efm8.crc(range(255)) == [5, 48]
    assert efm8.crc([]) == [0, 0]


def test_simple():
    """Simplest output."""
    assert efm8.to_frames([0], False, False) == [
        [36, 4, 49, 165, 241, 0],
        [36, 4, 50, 0, 0, 255],
        [36, 4, 51, 0, 0, 0],
    ]


def test_good():
    """Nothing to see here."""
    assert efm8.to_frames(efm8.read_intel_hex("tests/good.hex")) == [
        [36, 4, 49, 165, 241, 0],
        [
            36,
            35,
            50,
            0,
            0,
            255,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
        ],
        [36, 7, 52, 0, 0, 0, 31, 219, 216],
        [36, 4, 51, 0, 0, 0],
        [36, 3, 54, 0, 0],
    ]


def test_bad_checksum():
    """We must not accept malformed-input."""
    with pytest.raises(efm8.BadChecksum):
        efm8.read_intel_hex("tests/bad_checksum.hex")


def test_nonlinear():
    """Not implemented."""
    with pytest.raises(efm8.Unsupported):
        efm8.read_intel_hex("tests/nonlinear.hex")


def test_not_intel():
    """Common user error."""
    with pytest.raises(efm8.Unsupported):
        efm8.read_intel_hex("README.rst")


def test_not_empty():
    """Common user error."""
    with pytest.raises(efm8.Unsupported):
        efm8.read_intel_hex("tests/empty.hex")


@patch("efm8.hid")
def test_flash_null(hid):
    """Check null edge-case."""
    efm8.flash(1, 2, "3", [])
    hid.device().open.assert_called_once_with(1, 2, "3")


@patch("efm8.hid")
def test_flash(hid):
    """Check we happy case."""
    hid.device().get_feature_report.return_value = [64]
    efm8.flash(1, 2, "3", efm8.to_frames([0]))
    hid.device().open.assert_called_once_with(1, 2, "3")


@patch("efm8.hid")
def test_flash_error(hid):
    """Check we handle a error case."""
    hid.device().get_feature_report.return_value = [0]
    with pytest.raises(efm8.BadResponse):
        efm8.flash(1, 2, "3", efm8.to_frames([0]))
    hid.device().open.assert_called_once_with(1, 2, "3")


@patch("efm8.hid")
def test_flash_checksum(hid):
    """Check we handle a checksum-error case."""
    hid.device().get_feature_report.side_effect = [[64], [64], [63]]
    with pytest.raises(efm8.BadChecksum):
        efm8.flash(1, 2, "3", efm8.to_frames([0]))
    hid.device().open.assert_called_once_with(1, 2, "3")


@patch("efm8.hid")
def test_read_flash_null(hid):
    """Check we call hid correctly."""
    efm8.read_flash(1, 2, "3", 0)
    hid.device().open.assert_called_once_with(1, 2, "3")


@patch("efm8.hid")
def test_read_flash(hid):
    """Check we call hid correctly."""
    hid.device().get_feature_report.side_effect = [[64]] * 200 + [[63]] * 1000
    with pytest.raises(efm8.BadResponse):
        efm8.read_flash(1, 2, "3", 256)
    hid.device().open.assert_called_with(1, 2, "3")


def test_write_hex():
    """Check we can output Intel hex."""
    with patch(
        "__builtin__.open" if sys.version_info[0] == 2 else "efm8.open", mock_open()
    ) as mock_file:
        efm8.write_hex([0], "foo.hex")
        mock_file().write.assert_called_with(":00000001FF\n")


def test_main():
    """Check we can construct parser."""
    efm8_main._parser(True)
    efm8_main._parser(False)
    efm8.u2fzero._parser()


@patch("efm8.u2fzero.hid")
def test_u2fzero_reset(hid):
    """Check u2fzero."""
    efm8.u2fzero.reset(0x10C4, 0x8ACF, "foo")
    hid.device().open.assert_called_with(0x10C4, 0x8ACF, "foo")
    hid.device().write.assert_called_with([0, 255, 255, 255, 255, 136])
