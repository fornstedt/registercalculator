import tkinter as tk
from tkinter import ttk, Frame, END, INSERT, ANCHOR, SEL_FIRST, SEL_LAST
from string import hexdigits
from contextlib import suppress

DELIMITER = '_'


class RegCalcWindow:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.rowconfigure(0, minsize=20)
        self.root.rowconfigure(1, minsize=30)
        self.root.title('Register Calculator')

        self.topframe = Frame(self.root)
        self.topframe.pack(padx=1, pady=1)
        self.bottomframe = Frame(self.root)
        self.bottomframe.pack(padx=1, pady=1)
        
        
        self.hex_label = ttk.Label(self.topframe, text="Hex", borderwidth=5).grid(row=0, column=0)
        self.dec_label = ttk.Label(self.topframe, text="Dec", borderwidth=5).grid(row=0, column=2)

        self.hex_entry = ttk.Entry(self.topframe, width=8, justify='right', font='TkFixedFont', validate='key',
                                   validatecommand=(self.root.register(self.validate_hex), "%S", "%P", 32))
        self.dec_entry = ttk.Entry(self.topframe, width=10, justify='right', font='TkFixedFont', validate='key',
                                   validatecommand=(self.root.register(self.validate_dec), "%S", "%P", 32))
        self.bin_entry = ttk.Entry(self.topframe, width=39, justify='right', font='TkFixedFont', validate='key',
                                   validatecommand=(self.root.register(self.is_bin), "%S", "%P", 32 + 7))

        self.add_button = ttk.Button(self.topframe, text='Add field', width=15, state='disabled', command=self.add_field_button_click)

        self.hex_entry.bind('<Any-KeyRelease>',  lambda event: self.hex_keyrelease(self.hex_entry))
        self.dec_entry.bind('<Any-KeyRelease>', self.dec_keyrelease)
        self.bin_entry.bind('<Any-KeyRelease>', self.bin_keyrelease)
        self.bin_entry.bind('<Motion>', self.bin_mouse_motion)

        self.hex_entry.grid(row=0, column=1, padx=1, pady=1)
        self.dec_entry.grid(row=0, column=3, padx=1, pady=1)
        self.add_button.grid(row=0, column=4, padx=1, pady=1)
        self.bin_entry.grid(row=1, column=0, padx=3, pady=1, columnspan=5)

        self.field_selection = {'start': None, 'end': None}
        self.fields = []

        self.state = {}
        self.update_state(0)

    def update_state(self, value: int) -> None:
        self.state['value'] = value
        self.state['dec_string'] = f'{value}'
        self.state['hex_string'] = f'{value:X}'
        self.state['bin_string'] = f'{value:032b}'
        self.state['bin_string_delim'] = self.get_delimited_bin(value)
        self.update_gui_values()

    @staticmethod
    def get_delimited_bin(value: int) -> str:
        bin_value = f'{value:032b}'

        groups = []
        for i in range(0, len(bin_value), 4):
            groups.append(bin_value[i:i+4])
        bin_value = DELIMITER.join(groups)

        return bin_value

    def validate_dec(self, text_to_insert, all_text, bit_width):
        max_value = 2 ** int(bit_width) - 1
        max_width = len(str(max_value))
        return len(all_text) <= max_width and \
               text_to_insert.isdecimal() and \
               (all_text == '' or (int(all_text) <= max_value))

    def validate_hex(self, text_to_insert, all_text, bit_width):
        max_value = 2 ** int(bit_width) - 1
        max_width = len(str(max_value))
        value = int(self.hex_to_dec(all_text))

        return len(all_text) <= max_width and \
               all(c in hexdigits for c in text_to_insert) and \
               value <= max_value

    @staticmethod
    def is_bin(text_to_insert, all_text, bit_width):
        return len(all_text) <= int(bit_width) and all(c in '01' + DELIMITER for c in text_to_insert)

    def add_field_button_click(self):
        field = {}
        field['start'] = self.field_selection['start']
        field['end'] = self.field_selection['end']
        field['name'] = ''
        field['bit_length'] = field['start'] - field['end'] + 1
        field['max_value'] = 2 ** field['bit_length'] - 1
        field['mask'] = ~(field['max_value'] << field['end'])
        
        self.add_field(field)
        self.bin_entry.selection_clear()
        self.update_selection()
        self.update_add_field_button()

    def add_field(self, settings: dict):
        if len(self.fields) == 0:
            ttk.Label(self.bottomframe, text='Bits', borderwidth=5).grid(row=0, column=0, padx=1, pady=1)
            ttk.Label(self.bottomframe, text='Bin', borderwidth=5).grid(row=0, column=1, padx=1, pady=1, sticky='E')
            ttk.Label(self.bottomframe, text='Hex', borderwidth=5).grid(row=0, column=2, padx=1, pady=1, sticky='E')
            ttk.Label(self.bottomframe, text='Dec', borderwidth=5).grid(row=0, column=3, padx=1, pady=1, sticky='E')
            ttk.Label(self.bottomframe, text='Name', borderwidth=5).grid(row=0, column=4, padx=3, pady=1, sticky='W')

        bit_width = settings["start"] - settings["end"] + 1
        max_value = 2 ** int(bit_width) - 1
        max_hex_width = len(str(max_value))
        max_bin_width = len(str(max_value))
        gui = {'bit_label': ttk.Label(self.bottomframe, text=f'{settings["start"]}:{settings["end"]}', borderwidth=5),
               'bin_entry': ttk.Entry(self.bottomframe, width=bit_width, justify='right', font='TkFixedFont', validate='key',
                                      validatecommand=(self.root.register(self.is_bin), "%S", "%P", bit_width)),
               'hex_entry': ttk.Entry(self.bottomframe, width=max_hex_width, justify='right', font='TkFixedFont', validate='key',
                                      validatecommand=(self.root.register(self.validate_hex), "%S", "%P", bit_width)),
               'dec_entry': ttk.Entry(self.bottomframe, width=max_bin_width, justify='right', font='TkFixedFont', validate='key',
                                      validatecommand=(self.root.register(self.validate_dec), "%S", "%P", bit_width)),
               'name': ttk.Entry(self.bottomframe, width=20, justify='left', font='TkFixedFont')}

        field = {'settings': settings, 'gui': gui}

        field['gui']['hex_entry'].bind('<Any-KeyRelease>', lambda event: self.hex_field_keyrelease(field))
        field['gui']['dec_entry'].bind('<Any-KeyRelease>', lambda event: self.dec_field_keyrelease(field))
        field['gui']['bin_entry'].bind('<Any-KeyRelease>', lambda event: self.bin_field_keyrelease(field))
        
        next_row = len(self.fields) + 1
        field['gui']['bit_label'].grid(row=next_row, column=0, padx=1, pady=1)
        field['gui']['bin_entry'].grid(row=next_row, column=1, sticky='E', padx=3, pady=1)
        field['gui']['hex_entry'].grid(row=next_row, column=2, sticky='E', padx=3, pady=1)
        field['gui']['dec_entry'].grid(row=next_row, column=3, sticky='E', padx=3, pady=1)
        field['gui']['name'].grid(row=next_row, column=4, padx=3, pady=1, columnspan=2)

        self.fields.append(field)
        self.update_gui_values()
        
    def update_gui_values(self):
        self.set_text(self.dec_entry, self.state['dec_string'])
        self.set_text(self.bin_entry, self.state['bin_string_delim'])
        self.set_text(self.hex_entry, self.state['hex_string'])
        for field in self.fields:
            bin_start = 31 - field['settings']['start']
            bin_end = 32 - field['settings']['end']
            bin_string = self.state['bin_string'][bin_start:bin_end]
            self.set_text(field['gui']['bin_entry'], bin_string)
            self.set_text(field['gui']['dec_entry'], f'{int(bin_string, 2)}')
            self.set_text(field['gui']['hex_entry'], f'{int(bin_string, 2):X}')

    def bin_mouse_motion(self, event):
        self.update_selection()
        self.update_add_field_button()

    def update_selection(self):
        if self.bin_entry.selection_present():
            start_index = self.bin_entry.index(SEL_FIRST)
            end_index = self.bin_entry.index(SEL_LAST)

            delimiters_before_selection = self.bin_entry.get()[0:start_index].count(DELIMITER)
            delimiters_in_selection = self.bin_entry.get()[start_index:end_index].count(DELIMITER)

            start_index = 31 - (start_index - delimiters_before_selection)
            end_index = 32 - (end_index - delimiters_before_selection - delimiters_in_selection)

            self.field_selection['start'] = start_index
            self.field_selection['end'] = end_index
        else:
            self.field_selection['start'] = None
            self.field_selection['end'] = None

    def update_add_field_button(self):
        if self.field_selection['start'] is None or self.field_selection['end'] is None:
            self.add_button.configure(text='Add field', state='disabled')
        else:
            self.add_button.configure(text=f'Add field {self.field_selection["start"]}:{self.field_selection["end"]}',
                                      state='enabled')

    def hex_field_keyrelease(self, field):
        value_string = field['gui']['hex_entry'].get()
        field_value = (int(value_string, 16) if value_string != '' else 0) << field['settings']['end']
        value = (self.state['value'] & field['settings']['mask']) | field_value
        self.update_state(value)
        
    def dec_field_keyrelease(self, field):
        value_string = field['gui']['dec_entry'].get()
        field_value = (int(value_string) if value_string != '' else 0) << field['settings']['end']
        value = (self.state['value'] & field['settings']['mask']) | field_value
        self.update_state(value)
        
    def bin_field_keyrelease(self, field):
        value_string = field['gui']['bin_entry'].get()
        field_value = (int(value_string, 2) if value_string != '' else 0) << field['settings']['end']
        value = (self.state['value'] & field['settings']['mask']) | field_value
        self.update_state(value)
        
    def hex_keyrelease(self, entry):
        value_string = entry.get()
        value = int(value_string, 16) if value_string != '' else 0
        self.update_state(value)

    def dec_keyrelease(self, event):
        value_string = self.dec_entry.get()
        value = int(value_string) if value_string != '' else 0
        self.update_state(value)

    def bin_keyrelease(self, event):
        value_string = self.bin_entry.get()
        value = int(value_string.replace(DELIMITER, ""), 2) if value_string != '' else 0
        self.update_state(value)

    @staticmethod
    def dec_to_hex(value: str) -> str:
        hex_value = '0'
        with suppress(ValueError): hex_value = f'{int(value):X}'
        return hex_value

    @staticmethod
    def hex_to_dec(value: str) -> str:
        dec_value = '0'
        with suppress(ValueError): dec_value = f'{int(value, 16)}'
        return dec_value

    @staticmethod
    def dec_to_bin(value: str) -> str:
        with suppress(ValueError): bin_value = f'{int(value):032b}'

        if bin_value is not None:
            groups = []
            for i in range(0, len(bin_value), 4):
                groups.append(bin_value[i:i+4])
            bin_value = DELIMITER.join(groups)

        return bin_value

    @staticmethod
    def bin_to_dec(value: str) -> str:
        with suppress(ValueError): dec_value = f'{int(value.replace(DELIMITER, ""), 2)}'
        return dec_value

    @staticmethod
    def set_text(entry, text):
        index = entry.index(INSERT)
        entry.delete(0, END)
        entry.insert(0, text)
        entry.icursor(index)

    def show(self):
        self.root.mainloop()


def main():
    reg_calc_window = RegCalcWindow()
    reg_calc_window.show()


if __name__ == "__main__":
    main()
