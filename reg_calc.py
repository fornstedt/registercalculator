import sys
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, Frame, filedialog, END, INSERT, SEL_FIRST, SEL_LAST
from string import hexdigits
from contextlib import suppress

from register import Register, Field

DELIMITER = '_'
NAME_FIELD_WIDTH=30
BIT_LENGTHS=['8 bits', '16 bits', '32 bits']

class RegCalcWindow:
    def __init__(self) -> None:

        if sys.platform == 'darwin':
            self.right_click_button = '<Button-2>'
        else:
            self.right_click_button = '<Button-3>'

        self.register = Register()
        self.root = tk.Tk()
        self.root.rowconfigure(0, minsize=20)
        self.root.rowconfigure(1, minsize=30)
        self.root.title('Register Calculator')
        self.root.resizable(False, False)

        self.bit_length_string = tk.StringVar(self.root)
        self.bit_length_string.set(BIT_LENGTHS[2])

        self.topframe = Frame(self.root)
        self.topframe.pack(padx=1, pady=1)
        self.bottomframe = Frame(self.root)
        self.bottomframe.pack(padx=1, pady=1)

        ttk.Label(self.topframe, text="Hex", borderwidth=5).grid(row=0, column=0)
        ttk.Label(self.topframe, text="Dec", borderwidth=5).grid(row=0, column=2)

        self.hex_entry = ttk.Entry(self.topframe, width=8, justify='right', font='TkFixedFont', validate='key',
                                   validatecommand=(self.root.register(self.validate_hex), "%S", "%P", self.register.max_hex_width))
        self.dec_entry = ttk.Entry(self.topframe, width=10, justify='right', font='TkFixedFont', validate='key',
                                   validatecommand=(self.root.register(self.validate_dec), "%S", "%P", self.register.max_dec_width))
        self.bin_entry = ttk.Entry(self.topframe, width=39, justify='right', font='TkFixedFont', validate='key',
                                   validatecommand=(self.root.register(self.validate_bin), "%S", "%P", self.register.max_bin_width))

        self.add_button = ttk.Button(self.topframe, text='Add field', width=15, state='disabled', command=self.add_field_button_click)
        self.swap_button = ttk.Button(self.topframe, text='Swap bytes', width=15, state='enabled', command=self.swap_bytes_button_click)

        self.bit_length_menu = ttk.OptionMenu(self.topframe, self.bit_length_string, BIT_LENGTHS[2], *BIT_LENGTHS, command=self.bit_selection_clicked)

        self.hex_entry.bind('<Any-KeyRelease>',  lambda event: self.hex_keyrelease(self.hex_entry))
        self.dec_entry.bind('<Any-KeyRelease>', self.dec_keyrelease)
        self.bin_entry.bind('<Any-KeyRelease>', self.bin_keyrelease)
        self.bin_entry.bind('<Motion>', self.bin_mouse_motion)

        self.hex_entry.grid(row=0, column=1, padx=1, pady=1)
        self.dec_entry.grid(row=0, column=3, padx=1, pady=1)
        self.swap_button.grid(row=0, column=4, padx=1, pady=1)
        self.bit_length_menu.grid(row=0, column=5, padx=1, pady=1)
        self.bin_entry.grid(row=1, column=0, padx=3, pady=1, columnspan=5)
        self.add_button.grid(row=1, column=5, padx=1, pady=1)

        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label='Export fields', command=self.export_dialog)
        self.menu.add_command(label='Import fields', command=self.import_dialog)
        self.menu.add_separator()
        self.menu.add_command(label='Reset fields', command=self.reset_fields)
        self.root.bind(self.right_click_button, self.show_menu)
        self.bottomframe.bind('<Expose>', self.on_expose)

        self.field_selection = {'start': None, 'end': None}
        self.fields = []

        self.refresh_gui()

    def bit_selection_clicked(self, _):
        self.register.value = self.register.value & (2**self.register.bit_length - 1)
        self.refresh_gui()

    def swap_bytes_button_click(self):
        self.register.swap_bytes()
        self.refresh_gui()

    def on_expose(self, event):
        widget = event.widget
        if not widget.children:
            widget.configure(height=1)

    def reset_fields(self):
        for widget in self.bottomframe.winfo_children():
            widget.destroy()
        self.fields.clear()

    def export_dialog(self):
        if (export_file := filedialog.asksaveasfile(defaultextension='.json',
                                                    filetypes=[('JSON-files', '*.json'),
                                                               ('All files', '*.*')])) is not None:
            self.export_fields(export_file)
            export_file.close()
            self.root.title(Path(export_file.name).stem)

    def export_fields(self, file):
        export_fields = []
        for field in self.fields:
            export_fields.append(field['settings'])
        file.write(json.dumps(export_fields, indent=4))

    def import_dialog(self):
        if (import_file := filedialog.askopenfile(filetypes=[('JSON-files', '*.json'),
                                                             ('All files', '*.*')])) is not None:
            self.import_fields(import_file)
            import_file.close()
            self.root.title(Path(import_file.name).stem)

    def import_fields(self, file):
        self.reset_fields()
        import_fields = json.loads(file.read())
        for field in import_fields:
            self.add_field(field)

    def show_menu(self, event):
        try:
            self.menu.post(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def validate_dec(self, text_to_insert, all_text, width):
        return len(all_text) <= int(width) and text_to_insert.isdecimal() and (all_text == '' or (int(all_text) <= self.register.max))

    def validate_hex(self, text_to_insert, all_text, width):
        value = int(self.hex_to_dec(all_text))
        return len(all_text) <= int(width) and all(c in hexdigits for c in text_to_insert) and value <= self.register.max

    def validate_bin(self, text_to_insert, all_text, width):
        return len(all_text) <= (self.register.bit_length + self.register.bit_length // 4 - 1) and all(c in '01' + DELIMITER for c in text_to_insert)

    def add_field_button_click(self):
        field = Field(self.register, self.field_selection['start'], self.field_selection['end'])
        self.add_field(field)
        self.bin_entry.selection_clear()
        self.update_selection()
        self.update_add_field_button()

    def add_field(self, field: Field):
        if len(self.fields) == 0:
            ttk.Label(self.bottomframe, text='Bits', borderwidth=5).grid(row=0, column=0, padx=1, pady=1)
            ttk.Label(self.bottomframe, text='Bin', borderwidth=5).grid(row=0, column=1, padx=1, pady=1, sticky='E')
            ttk.Label(self.bottomframe, text='Hex', borderwidth=5).grid(row=0, column=2, padx=1, pady=1, sticky='E')
            ttk.Label(self.bottomframe, text='Dec', borderwidth=5).grid(row=0, column=3, padx=1, pady=1, sticky='E')
            ttk.Label(self.bottomframe, text='Name', borderwidth=5).grid(row=0, column=4, padx=3, pady=1, sticky='W')

        gui = {'bit_label': ttk.Label(self.bottomframe, text=f'{field.start}:{field.end}', borderwidth=5),
               'bin_entry': ttk.Entry(self.bottomframe, width=field.max_bin_width, justify='right', font='TkFixedFont', validate='key',
                                      validatecommand=(self.root.register(self.validate_bin), "%S", "%P", field.max_bin_width)),
               'hex_entry': ttk.Entry(self.bottomframe, width=field.max_hex_width, justify='right', font='TkFixedFont', validate='key',
                                      validatecommand=(self.root.register(self.validate_hex), "%S", "%P", field.max_hex_width)),
               'dec_entry': ttk.Entry(self.bottomframe, width=field.max_dec_width, justify='right', font='TkFixedFont', validate='key',
                                      validatecommand=(self.root.register(self.validate_dec), "%S", "%P", field.max_dec_width)),
               'name': ttk.Entry(self.bottomframe, width=NAME_FIELD_WIDTH, justify='left', font='TkFixedFont')}

        field_gui = {'field': field, 'gui': gui}

        field_gui['gui']['hex_entry'].bind('<Any-KeyRelease>', lambda event: self.hex_field_keyrelease(field_gui))
        field_gui['gui']['dec_entry'].bind('<Any-KeyRelease>', lambda event: self.dec_field_keyrelease(field_gui))
        field_gui['gui']['bin_entry'].bind('<Any-KeyRelease>', lambda event: self.bin_field_keyrelease(field_gui))
        field_gui['gui']['name'].bind('<Any-KeyRelease>', lambda event: self.name_field_keyrelease(field_gui))

        next_row = len(self.fields) + 1
        field_gui['gui']['bit_label'].grid(row=next_row, column=0, padx=1, pady=1)
        field_gui['gui']['bin_entry'].grid(row=next_row, column=1, sticky='E', padx=3, pady=1)
        field_gui['gui']['hex_entry'].grid(row=next_row, column=2, sticky='E', padx=3, pady=1)
        field_gui['gui']['dec_entry'].grid(row=next_row, column=3, sticky='E', padx=3, pady=1)
        field_gui['gui']['name'].grid(row=next_row, column=4, sticky='W', padx=3, pady=1, columnspan=2)

        self.fields.append(field_gui)
        self.refresh_gui()

    def refresh_gui(self):
        self.set_text(self.dec_entry, self.register.dec)
        self.set_text(self.bin_entry, self.register.bin_delimited)
        self.set_text(self.hex_entry, self.register.hex)
        for field in self.fields:
            try:
                self.set_text(field['gui']['bin_entry'], field['field'].bin)
                self.set_text(field['gui']['dec_entry'], field['field'].dec)
                self.set_text(field['gui']['hex_entry'], field['field'].hex)
                self.set_text(field['gui']['name'], 'Not Implemented')
                self.adjust_entry_length(field['gui']['name'])
            except ValueError:
                field['gui']['bin_entry'].config(state = 'disabled')
                field['gui']['dec_entry'].config(state = 'disabled')
                field['gui']['hex_entry'].config(state = 'disabled')
                field['gui']['name'].config(state = 'disabled')

    def bin_mouse_motion(self, _):
        self.update_selection()
        self.update_add_field_button()

    def update_selection(self):
        if self.bin_entry.selection_present():
            start_index = self.bin_entry.index(SEL_FIRST)
            end_index = self.bin_entry.index(SEL_LAST)

            delimiters_before_selection = self.bin_entry.get()[0:start_index].count(DELIMITER)
            delimiters_in_selection = self.bin_entry.get()[start_index:end_index].count(DELIMITER)

            start_index = self.register.bit_length - (start_index - delimiters_before_selection) - 1
            end_index = self.register.bit_length - (end_index - delimiters_before_selection - delimiters_in_selection)

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

    def adjust_entry_length(self, entry, minimum=NAME_FIELD_WIDTH):
        length = len(entry.get())
        if length > minimum:
            entry.configure(width=length)

    def hex_field_keyrelease(self, field):
        value_string = field['gui']['hex_entry'].get()
        field['field'].value = int(value_string, 16) if value_string != '' else 0
        self.refresh_gui()

    def dec_field_keyrelease(self, field):
        value_string = field['gui']['dec_entry'].get()
        field['field'].value = int(value_string) if value_string != '' else 0
        self.refresh_gui()

    def bin_field_keyrelease(self, field):
        value_string = field['gui']['bin_entry'].get()
        field['field'].value = int(value_string, 2) if value_string != '' else 0
        self.refresh_gui()

    def name_field_keyrelease(self, field):
        #field['settings']['name'] = field['gui']['name'].get()
        #self.adjust_entry_length(field['gui']['name'])
        pass

    def hex_keyrelease(self, entry):
        value_string = entry.get()
        self.register.value = int(value_string, 16) if value_string != '' else 0
        self.refresh_gui()

    def dec_keyrelease(self, event):
        value_string = self.dec_entry.get()
        self.register.value = int(value_string) if value_string != '' else 0
        self.refresh_gui()

    def bin_keyrelease(self, event):
        value_string = self.bin_entry.get()
        self.register.value = int(value_string.replace(DELIMITER, ""), 2) if value_string != '' else 0
        self.refresh_gui()

    @staticmethod
    def hex_to_dec(value: str) -> str:
        dec_value = '0'
        with suppress(ValueError): dec_value = f'{int(value, 16)}'
        return dec_value

    @staticmethod
    def set_text(entry, text):
        index = entry.index(INSERT)
        entry.config(state='enabled')
        entry.delete(0, END)
        entry.insert(0, text)
        entry.icursor(index)

    def show(self):
        self.root.mainloop()


def main(import_filepath = None):
    main_window = RegCalcWindow()

    if import_filepath:
        with open(import_filepath, 'r', encoding='utf-8') as import_file:
            main_window.import_fields(import_file)

    main_window.show()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
