"""Module for handling data registers and register fieldss"""

from abc import ABC, abstractmethod

DELIMITER = '_'


class DataRegisterBase(ABC):
    """Abstract class with common functionality for both registers and register fields"""
    def __init__(self, bit_length: int) -> None:
        self._bit_length = bit_length

    @property
    @abstractmethod
    def value(self) -> int:
        """The current value"""

    @property
    def bit_length(self) -> int:
        """The bit length of the maximum value"""
        return self._bit_length

    @property
    def dec(self) -> str:
        """Return the decimal string representing current value"""
        return f'{self.value}'

    @property
    def hex(self) -> str:
        """Return the hexadecimal string representing current value"""
        return f'{self.value:X}'

    @property
    def bin(self) -> str:
        """Return the binary string representing current value"""
        return f'{self.value:0{self._bit_length}b}'

    @property
    def bin_delimited(self) -> str:
        """Return the hexadecimal string representing current value, delimited each fourth bit"""
        string = self.bin

        groups = []
        for i in range(0, len(string), 4):
            groups.append(string[i:i+4])
        string = DELIMITER.join(groups)

        return string

    @property
    def max(self) -> int:
        """Max value of the register or field"""
        return (2 ** self._bit_length) - 1

    @property
    def max_dec_width(self) -> int:
        """The maximum decimal value string width"""
        return len(f'{self.max}')

    @property
    def max_hex_width(self) -> int:
        """The maximum hexadecimal value string width"""
        return len(f'{self.max:X}')

    @property
    def max_bin_width(self) -> int:
        """The maximum binary value string width"""
        return self._bit_length


class DataRegister(DataRegisterBase):
    """Class to handle a data register"""

    def __init__(self, value=0, bit_length=32) -> None:
        super().__init__(bit_length)
        self._register_value = value
        self._observers = []
        self.bit_length = bit_length

    @property
    def value(self) -> int:
        return self._register_value

    @value.setter
    def value(self, value: int) -> None:
        self._register_value = value
        self._truncate()
        self.notify_observers()

    @DataRegisterBase.bit_length.setter
    def bit_length(self, bit_length: int) -> None:
        if bit_length in [8, 16, 32]:
            self._bit_length = bit_length
            self._truncate()
        else:
            raise ValueError('Bit length must be 8, 16 or 32')
        self.notify_observers()

    def swap_bytes(self) -> None:
        """Swap all bytes of the current value."""
        if self._bit_length == 16:
            self._register_value = (((self._register_value >> 0x08) & 0x00FF) |
                                    ((self._register_value << 0x08) & 0xFF00))
        elif self._bit_length == 32:
            self._register_value = (((self._register_value >> 0x18) & 0x000000FF) |
                                    ((self._register_value << 0x08) & 0x00FF0000) |
                                    ((self._register_value >> 0x08) & 0x0000FF00) |
                                    ((self._register_value << 0x18) & 0xFF000000))
        else:
            pass
        self.notify_observers()

    def _truncate(self) -> None:
        self._register_value = self._register_value & self.max

    def register_observer(self, callback):
        """Register a callback to be called when the register value is changed."""
        self._observers.append(callback)

    def unregister_observer(self, callback):
        """Unregister a callback"""
        self._observers.remove(callback)

    def notify_observers(self):
        """Notify all observers about a value change"""
        for callback in self._observers:
            callback()


class DataField(DataRegisterBase):
    """Class to handle a data register field"""

    def __init__(self, register: DataRegister, start_bit: int, end_bit: int) -> None:
        if ((start_bit > register.bit_length - 1) or (start_bit < 0) or
           (end_bit < 0) or (end_bit > start_bit)):
            raise ValueError('Invalid bit configuration.')

        self._register = register

        self._start_bit = start_bit
        self._end_bit = end_bit
        self._bit_length = start_bit - end_bit + 1
        self._mask = self.max << self._end_bit
        super().__init__(bit_length=self._bit_length)

    @property
    def value(self) -> int:
        if self._start_bit < self._register.bit_length:
            return (self._register.value & self._mask) >> self._end_bit
        else:
            raise ValueError("Field is not within its register's bit length.")

    @value.setter
    def value(self, value: int) -> None:
        if value <= self.max:
            self._register.value = (self._register.value & ~self._mask) | (value << self._end_bit)
        else:
            raise ValueError('Value cannot fit into field.')

    @property
    def start_bit(self):
        """Return the number of the first bit included in the field"""
        return self._start_bit

    @property
    def end_bit(self):
        """Return the number of the last bit included in the field"""
        return self._end_bit

    def register_observer(self, callback) -> None:
        """Register a callback to be called when the register value is changed."""
        self._register.register_observer(callback)

    def unregister_observer(self, callback) -> None:
        """UnRegister a callback."""
        self._register.unregister_observer(callback)
