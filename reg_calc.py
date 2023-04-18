import sys
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, Frame, filedialog, SEL_FIRST, SEL_LAST

from register import Register, DELIMITER
from gui_extensions import BinEntry, DecEntry, HexEntry, GuiField

BIT_LENGTHS = ['8 bits', '16 bits', '32 bits']


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

        self.hex_entry = HexEntry(self.topframe, self.register)
        self.dec_entry = DecEntry(self.topframe, self.register)
        self.bin_entry = BinEntry(self.topframe, self.register, with_delimiter=True)

        self.add_button = ttk.Button(self.topframe, text='Add field', width=15, state='disabled',
                                     command=self._add_field_button_click)
        self.swap_button = ttk.Button(self.topframe, text='Swap bytes', width=15, state='enabled',
                                      command=self._swap_bytes_button_click)

        self.bit_length_menu = ttk.OptionMenu(self.topframe, self.bit_length_string, BIT_LENGTHS[2],
                                              *BIT_LENGTHS, command=self._bit_selection_clicked)

        self.bin_entry.bind('<Motion>', self._mouse_motion)

        self.hex_entry.grid(row=0, column=1, padx=1, pady=1)
        self.dec_entry.grid(row=0, column=3, padx=1, pady=1)
        self.swap_button.grid(row=0, column=4, padx=1, pady=1)
        self.bit_length_menu.grid(row=0, column=5, padx=1, pady=1)
        self.bin_entry.grid(row=1, column=0, padx=3, pady=1, columnspan=5)
        self.add_button.grid(row=1, column=5, padx=1, pady=1)

        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label='Export fields', command=self._export_dialog)
        self.menu.add_command(label='Import fields', command=self._import_dialog)
        self.menu.add_separator()
        self.menu.add_command(label='Reset fields', command=self._reset_fields)
        self.root.bind(self.right_click_button, self._show_menu)
        self.bottomframe.bind('<Expose>', self._on_expose)

        self.field_selection = {'start': None, 'end': None}
        self.fields = []

        self._refresh_gui()

    @property
    def _number_of_bits(self):
        return 2**(BIT_LENGTHS.index(self.bit_length_string.get()) + 3)

    def _bit_selection_clicked(self, _):
        self.register.bit_length = self._number_of_bits
        self.swap_button.configure(state='disabled' if self.register.bit_length == 8 else 'enabled')
        self._refresh_gui()

    def _swap_bytes_button_click(self):
        self.register.swap_bytes()
        self._refresh_gui()

    def _on_expose(self, event):
        widget = event.widget
        if not widget.children:
            widget.configure(height=1)

    def _reset_fields(self):
        for field in self.fields:
            field.unregister()
        self.fields.clear()

        for widget in self.bottomframe.winfo_children():
            widget.destroy()

    def _export_dialog(self):
        if (export_file := filedialog.asksaveasfile(defaultextension='.json',
                                                    filetypes=[('JSON-files', '*.json'),
                                                               ('All files', '*.*')])) is not None:
            self._export_fields(export_file)
            export_file.close()
            self.root.title(Path(export_file.name).stem)

    def _export_fields(self, file):
        export_fields = []
        for field in self.fields:
            export_fields.append(field.settings)
        file.write(json.dumps(export_fields, indent=4))

    def _import_dialog(self):
        if (import_file := filedialog.askopenfile(filetypes=[('JSON-files', '*.json'),
                                                             ('All files', '*.*')])) is not None:
            self._import_fields(import_file)
            import_file.close()
            self.root.title(Path(import_file.name).stem)

    def _import_fields(self, file):
        self._reset_fields()
        import_fields = json.loads(file.read())
        for field in import_fields:
            self._add_field(field['start'], field['end'], field['name'])

    def _show_menu(self, event):
        try:
            self.menu.post(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def _add_field_button_click(self):
        self._add_field(self.field_selection['start'], self.field_selection['end'])
        self.bin_entry.selection_clear()
        self._update_selection()
        self._update_add_field_button()

    def _add_field(self, start_bit: int, end_bit: int, name=None):
        if len(self.fields) == 0:
            ttk.Label(self.bottomframe, text='Bits', borderwidth=5).grid(row=0, column=0, padx=1, pady=1)
            ttk.Label(self.bottomframe, text='Bin', borderwidth=5).grid(row=0, column=1, padx=1, pady=1, sticky='E')
            ttk.Label(self.bottomframe, text='Hex', borderwidth=5).grid(row=0, column=2, padx=1, pady=1, sticky='E')
            ttk.Label(self.bottomframe, text='Dec', borderwidth=5).grid(row=0, column=3, padx=1, pady=1, sticky='E')
            ttk.Label(self.bottomframe, text='Name', borderwidth=5).grid(row=0, column=4, padx=3, pady=1, sticky='W')

        next_row = len(self.fields) + 1
        gui_field = GuiField(self.bottomframe, self.register, start_bit, end_bit, name)
        gui_field.grid(next_row)
        self.fields.append(gui_field)

    def _refresh_gui(self):
        self.register.notify_observers()

    def _mouse_motion(self, _):
        self._update_selection()
        self._update_add_field_button()

    def _update_selection(self):
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

    def _update_add_field_button(self):
        if self.field_selection['start'] is None or self.field_selection['end'] is None:
            self.add_button.configure(text='Add field', state='disabled')
        else:
            self.add_button.configure(text=f'Add field {self.field_selection["start"]}:{self.field_selection["end"]}',
                                      state='enabled')

    def show(self):
        """Show the main window"""
        self.root.mainloop()


def start_register_calculator(import_filepath=None):
    main_window = RegCalcWindow()

    if import_filepath:
        with open(import_filepath, 'r', encoding='utf-8') as import_file:
            main_window._import_fields(import_file)

    main_window.show()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        start_register_calculator(sys.argv[1])
    else:
        start_register_calculator()
