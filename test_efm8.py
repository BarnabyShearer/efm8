"""Test file parsing and framing (but not hardware communication)"""

import pytest
import efm8

def test_twos():
    """Test exepcted outputs"""
    assert efm8.twos_complement(0xE2) == 0x1E
    assert efm8.twos_complement(0xFF) == 0x01
    assert efm8.twos_complement(0x00) == 0x00
    assert efm8.twos_complement(0x80) == 0x80

def test_toaddr():
    """Test exepcted outputs"""
    assert efm8.toaddr(0xFFFF) == [0xFF, 0xFF]
    assert efm8.toaddr(0x0102) == [0x01, 0x02]
    assert efm8.toaddr(0x0000) == [0x00, 0x00]

def test_crc():
    """Test exepcted outputs"""
    assert efm8.crc(range(255)) == [5, 48]
    assert efm8.crc([]) == [0, 0]

def test_good():
    """Nothing to see here"""
    assert efm8.to_frames(
        efm8.read_intel_hex(
            "tests/good.hex"
        )
    ) == [
        [36, 4, 49, 165, 241, 0],
        [
            36, 35, 50, 0, 0,
            255, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
            0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15
        ],
        [36, 7, 52, 0, 0, 0, 31, 219, 216],
        [36, 4, 51, 0, 0, 0],
        [36, 3, 54, 0, 0]
    ]

def test_bad_checksum():
    """We must not accept malformed-input"""
    with pytest.raises(efm8.BadChecksum):
        efm8.read_intel_hex(
            "tests/bad_checksum.hex"
        )

def test_nonlinear():
    """Not implemented"""
    with pytest.raises(efm8.Unsupported):
        efm8.read_intel_hex(
            "tests/nonlinear.hex"
        )

def test_not_intel():
    """Common user error"""
    with pytest.raises(efm8.Unsupported):
        efm8.read_intel_hex(
            "efm8.py"
        )
