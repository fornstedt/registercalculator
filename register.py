DELIMITER = '_'

class RegisterState:
    def __init__(self, value=0, bit_length=32):
        self._value = value
        self._bit_length = bit_length

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        self._value = value
        self._truncate()

    @property
    def bit_length(self):
        return self._bit_length
    
    @bit_length.setter
    def bit_length(self, bit_length):
        if bit_length in [8, 16, 32]:
            self._bit_length = bit_length
            self._truncate()
        else:
            raise ValueError('Bit length must be 8, 16 or 32')

    @property
    def dec_string(self):
        return f'{self._value}'
        
    @property
    def hex_string(self):
        return f'{self._value:X}'
    
    @property
    def bin_string(self):
        return f'{self._value:0{self._bit_length}b}'
    
    @property
    def bin_string_delim(self):
        string = self.bin_string

        groups = []
        for i in range(0, len(string), 4):
            groups.append(string[i:i+4])
        string = DELIMITER.join(groups)

        return string

    @property
    def max_value(self):
        return (2 ** self._bit_length) - 1
        
    def swap_bytes(self):
        if self._bit_length == 16:
            self._value = (((self._value >> 8) & 0x00FF) | \
                           ((self._value << 8) & 0xFF00))
        elif self._bit_length == 32:
            self._value = (((self._value >> 24) & 0x000000FF) | \
                           ((self._value <<  8) & 0x00FF0000) | \
                           ((self._value >>  8) & 0x0000FF00) | \
                           ((self._value << 24) & 0xFF000000))
        else:
            pass
        
    def _truncate(self):
        self._value = self._value & self.max_value


class RegisterField:
    def __init__(self, register, start_bit, end_bit):
        self.register = register
        self.start_bit = start_bit
        self.end_bit = end_bit
    
    @property
    def value(self):
        return self.register.value