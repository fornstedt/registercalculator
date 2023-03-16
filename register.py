DELIMITER = '_'


class RegisterBase:
    def __init__(self, value: int, bit_length: int) -> None:
        self._value = value
        self._bit_length = bit_length

    @property
    def bit_length(self) -> int:
        return self._bit_length

    @property
    def dec(self) -> str:
        return f'{self._value}'

    @property
    def hex(self) -> str:
        return f'{self._value:X}'

    @property
    def bin(self) -> str:
        return f'{self._value:0{self._bit_length}b}'

    @property
    def bin_delimited(self) -> str:
        string = self.bin

        groups = []
        for i in range(0, len(string), 4):
            groups.append(string[i:i+4])
        string = DELIMITER.join(groups)

        return string

    @property
    def max(self) -> int:
        return (2 ** self._bit_length) - 1

    @property
    def max_dec_width(self) -> int:
        return len(f'{self.max}')

    @property
    def max_hex_width(self) -> int:
        return len(f'{self.max:X}')

    @property
    def max_bin_width(self) -> int:
        return self._bit_length


class Register(RegisterBase):
    def __init__(self, value=0, bit_length=32) -> None:
        super().__init__(value, bit_length)
        self.bit_length = bit_length
        self.fields = []

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        self._value = value
        self._truncate()
        for field in self.fields:
            field.update_value()

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
        self._value = self._value & self.max

    def _register_field(self, field) -> None:
        self.fields.append(field)

    def clear_fields(self) -> None:
        self.fields.clear()


class Field(RegisterBase):
    def __init__(self, register: Register, start_bit: int, end_bit: int) -> None:
        if ((start_bit > register.bit_length) or (start_bit < 0) or
           (end_bit < 0) or (end_bit > start_bit)):
            raise ValueError('Invalid bit configuration.')

        self._register = register

        self._start_bit = start_bit
        self._end_bit = end_bit
        self._bit_length = start_bit - end_bit + 1
        self._mask = self.max << self._end_bit
        super().__init__(self.value, bit_length=self._bit_length)
        self._register._register_field(self)

    @property
    def value(self) -> int:
        if self._start_bit < self._register.bit_length:
            return (self._register.value & self._mask) >> self._end_bit
        else:
            raise ValueError("Field is not within its register's bit length.")

    @value.setter
    def value(self, value):
        if value <= self.max:
            self._register.value = (self._register.value & ~self._mask) | (value << self._end_bit)
        else:
            raise ValueError('Value cannot fit into field.')

    @property
    def start(self):
        return self._start_bit

    @property
    def end(self):
        return self._end_bit

    def update_value(self):
        self._value = (self._register.value & self._mask) >> self._end_bit
