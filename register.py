DELIMITER = '_'


class RegisterBase:
    def __init__(self, value: int, bit_length: int) -> None:
        self._value = value
        self._bit_length = bit_length

    @property
    def bit_length(self) -> int:
        return self._bit_length

    @property
    def dec_string(self) -> str:
        return f'{self._value}'

    @property
    def hex_string(self) -> str:
        return f'{self._value:X}'

    @property
    def bin_string(self) -> str:
        return f'{self._value:0{self._bit_length}b}'

    @property
    def bin_string_delim(self) -> str:
        string = self.bin_string

        groups = []
        for i in range(0, len(string), 4):
            groups.append(string[i:i+4])
        string = DELIMITER.join(groups)

        return string

    @property
    def max_value(self) -> int:
        return (2 ** self._bit_length) - 1


class Register(RegisterBase):
    def __init__(self, value=0, bit_length=32) -> None:
        super().__init__(value, bit_length)
        self.bit_length = bit_length

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        self._value = value
        self._truncate()

    @RegisterBase.bit_length.setter
    def bit_length(self, bit_length: int) -> None:
        if bit_length in [8, 16, 32]:
            self._bit_length = bit_length
            self._truncate()
        else:
            raise ValueError('Bit length must be 8, 16 or 32')

    def swap_bytes(self) -> None:
        if self._bit_length == 16:
            self._value = (((self._value >> 0x08) & 0x00FF) |
                           ((self._value << 0x08) & 0xFF00))
        elif self._bit_length == 32:
            self._value = (((self._value >> 0x18) & 0x000000FF) |
                           ((self._value << 0x08) & 0x00FF0000) |
                           ((self._value >> 0x08) & 0x0000FF00) |
                           ((self._value << 0x18) & 0xFF000000))
        else:
            pass

    def _truncate(self) -> None:
        self._value = self._value & self.max_value


class Field(RegisterBase):
    def __init__(self, register: Register, start_bit: int, end_bit: int) -> None:
        if ((start_bit > register.bit_length) or (start_bit < 0) or
           (end_bit < 0) or (end_bit > start_bit)):
            raise ValueError('Invalid bit configuration.')

        self._register = register

        self._start_bit = start_bit
        self._end_bit = end_bit
        self._bit_length = start_bit - end_bit + 1
        self._mask = self.max_value << self._end_bit
        super().__init__(self.value, bit_length=self._bit_length)

    @property
    def value(self) -> int:
        if self._start_bit < self._register.bit_length:
            return (self._register.value & self._mask) >> self._end_bit
        else:
            raise ValueError("Field is not within its register's bit length.")

    @value.setter
    def value(self, value):
        if value <= self.max_value:
            self._register.value = (self._register.value & ~self._mask) | (value << self._end_bit)
        else:
            raise ValueError('Value cannot fit into field.')
