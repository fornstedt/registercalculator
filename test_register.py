import pytest
from register import Register, Field


def test_register_strings():
    reg = Register()
    reg.value = 0x11223344
    assert reg.value == 0x11223344
    assert reg.dec == '287454020'
    assert reg.hex == '11223344'
    assert reg.bin == '00010001001000100011001101000100'
    assert reg.bin_delimited == '0001_0001_0010_0010_0011_0011_0100_0100'


def test_register_bit_lengths():
    reg = Register()
    reg.value = 0x11223344
    assert reg.max == 0xFFFFFFFF
    assert reg.bit_length == 32

    reg.bit_length = 16
    assert reg.bit_length == 16
    assert reg.max == 0xFFFF
    assert reg.value == 0x3344
    assert reg.bin == '0011001101000100'

    reg.bit_length = 8
    assert reg.bit_length == 8
    assert reg.max == 0xFF
    assert reg.value == 0x44
    assert reg.bin == '01000100'

    reg = Register(0x11223344, 16)
    assert reg.value == 0x3344

    reg.value = 0x11223344
    assert reg.value == 0x3344

    reg.bit_length = 32
    assert reg.bit_length == 32
    reg.value = 0x11223344
    assert reg.max == 0xFFFFFFFF
    assert reg.value == 0x11223344

    with pytest.raises(ValueError):
        reg.bit_length = 23
    assert reg.bit_length == 32
    assert reg.value == 0x11223344


def test_register_byte_swap():
    reg = Register(0x11223344)
    assert reg.value == 0x11223344

    reg.swap_bytes()
    assert reg.value == 0x44332211

    reg.bit_length = 16
    reg.swap_bytes()
    assert reg.value == 0x1122

    reg.bit_length = 8
    reg.swap_bytes()
    assert reg.value == 0x22


def test_field_strings():
    reg = Register(0x11223344)
    field = Field(reg, 15, 8)
    assert field.start_bit == 15
    assert field.end_bit == 8

    assert field.value == 0x33
    assert field.dec == '51'
    assert field.hex == '33'
    assert field.bin == '00110011'
    assert field.bin_delimited == '0011_0011'

    reg.value = 0xaabbccdd
    assert field.value == 0xcc
    assert field.dec == '204'
    assert field.hex == 'CC'
    assert field.bin == '11001100'
    assert field.bin_delimited == '1100_1100'

    assert field.max_dec_width == 3
    assert field.max_hex_width == 2
    assert field.max_bin_width == 8


def test_field_bit_lengths():
    reg = Register(0x11223344)
    field = Field(reg, 15, 8)
    assert field.bit_length == 8

    with pytest.raises(AttributeError):
        field.bit_length = 5

    assert field.max == 0xFF


def test_field_bit_positions():
    reg = Register(0x11223344)

    with pytest.raises(ValueError):
        _ = Field(reg, 32, 8)

    with pytest.raises(ValueError):
        _ = Field(reg, 31, -8)

    with pytest.raises(ValueError):
        _ = Field(reg, 20, 21)

    with pytest.raises(ValueError):
        _ = Field(reg, -8, -16)

    with pytest.raises(ValueError):
        _ = Field(reg, -8, 2)


def test_field_registry_changes():
    reg = Register(0x11223344)
    field = Field(reg, 23, 16)
    assert field.value == 0x22

    reg.value = 0xaabbccdd
    assert field.value == 0xbb

    reg.bit_length = 16
    with pytest.raises(ValueError):
        _ = field.value

    reg.bit_length = 32
    assert field.value == 0x00
    reg.value = 0xaabbccdd
    assert field.value == 0xbb


def test_field_value_changes():
    reg = Register(0x11223344)
    field = Field(reg, 23, 16)
    assert field.value == 0x22

    field.value = 0xbb
    assert reg.value == 0x11bb3344

    with pytest.raises(ValueError):
        field.value = 0x1FF
