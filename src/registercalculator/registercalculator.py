"""A tk based GUI to view and manipulate a register with fields"""

import json
import sys
import tkinter as tk
import webbrowser
from math import log
from pathlib import Path
from tkinter import Frame, filedialog, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD

from registercalculator.register import DataRegister

from .gui_extensions import BinEntry, DecEntry, FieldGui, HexEntry, AddButton

VERSION = "1.1"
BIT_LENGTHS = ["8 bits", "16 bits", "32 bits"]


class RegisterCalculator:
    """A register calculator GUI"""

    def __init__(self, import_filepath=None) -> None:
        if sys.platform == "darwin":
            self.right_click_button = "<Button-2>"
            self.swap_button_width = 8
            self.add_button_width = 16
            self.bit_button_width = 16
            self.bit_menu_width = 7
        else:
            self.right_click_button = "<Button-3>"
            self.swap_button_width = 10
            self.add_button_width = 21
            self.bit_button_width = 21
            self.bit_menu_width = 6

        self.window_title = "Register Calculator"

        # Setup main window
        self.register = DataRegister()
        self.root = TkinterDnD.Tk()
        self.root.rowconfigure(0, minsize=20)
        self.root.rowconfigure(1, minsize=30)
        self.root.title(self.window_title)
        self.root.resizable(False, False)

        # Allow dropping of files onto the main window
        self.root.drop_target_register(DND_FILES)

        # Bind the drop event to a handler
        self.root.dnd_bind("<<Drop>>", self.drop)

        self.topframe = Frame(self.root)
        self.topframe.pack(padx=1, pady=1)
        self.bottomframe = Frame(self.root)
        self.bottomframe.pack(padx=1, pady=1)

        # Entry labels
        self.hex_label = ttk.Label(self.topframe, text="Hex", borderwidth=5)
        self.dec_label = ttk.Label(self.topframe, text="Dec", borderwidth=5)
        self.bin_numbering = ttk.Label(
            self.topframe,
            text=self._get_numbering_label(),
            borderwidth=0,
            font="TkFixedFont",
            justify="right",
        )

        # Hex, dec and bin entries
        self.hex_entry = HexEntry(self.topframe, self.register)
        self.dec_entry = DecEntry(self.topframe, self.register)
        self.bin_entry = BinEntry(self.topframe, self.register, with_delimiter=True)

        # Byte swap button and a button to add new fields
        self.add_button = AddButton(
            master=self.topframe,
            width=self.add_button_width,
            command=self._add_field_button_click,
        )
        self.swap_button = ttk.Button(
            master=self.topframe,
            text="Swap bytes",
            width=self.swap_button_width,
            state="enabled",
            command=self._swap_bytes_button_click,
        )
        self.bit_button = ttk.Button(
            master=self.topframe,
            width=self.bit_button_width,
            state="enabled",
            command=self._bit_order_button_click,
        )

        # Dropdown for number of bits
        self.bit_length_string = tk.StringVar(self.root)
        self.bit_length_string.set(BIT_LENGTHS[2])
        self.bit_length_menu = ttk.OptionMenu(
            self.topframe,
            self.bit_length_string,
            BIT_LENGTHS[2],
            *BIT_LENGTHS,
            command=self._bit_selection_clicked,
        )
        self.bit_length_menu.config(width=self.bit_menu_width)

        # Bind mouse movement to handle selection of bits
        self.bin_entry.bind("<Motion>", self._mouse_motion)

        # Gui layout
        self.hex_label.grid(row=0, column=0, sticky="E")
        self.hex_entry.grid(row=0, column=1, padx=1, pady=1)
        self.dec_label.grid(row=0, column=2, sticky="E")
        self.dec_entry.grid(row=0, column=3, padx=1, pady=1)
        self.swap_button.grid(row=0, column=4, padx=1, pady=1)
        self.bit_button.grid(row=0, column=5, padx=1, pady=1)
        self.bin_entry.grid(row=1, column=0, padx=3, pady=0, columnspan=4)
        self.bit_length_menu.grid(row=1, column=4, padx=1, pady=0)
        self.add_button.grid(row=1, column=5, padx=1, pady=0)
        self.bin_numbering.grid(row=2, column=0, padx=3, pady=0, columnspan=4)

        # Import/export menu
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Export fields", command=self._export_dialog)
        self.menu.add_command(label="Import fields", command=self._import_dialog)
        self.menu.add_command(label="Reset fields", command=self._reset_fields)
        self.menu.add_separator()
        self.menu.add_command(label="Sort fields", command=self._sort_fields)
        self.menu.add_separator()
        self.menu.add_command(label="About...", command=self._show_about_popup)
        self.root.bind(self.right_click_button, self._show_menu)
        self.bottomframe.bind("<Expose>", self._on_expose)

        # Reset selection, clear fields and update all entries
        self.fields = []

        self.bin_entry.register_observer(self.add_button.update_selection_label)

        if import_filepath:
            with open(import_filepath, "r", encoding="utf-8") as import_file:
                self._import_fields(import_file)
        else:
            self._update_bit_button()
            self.register.notify_observers()

    def drop(self, event):
        # event.data contains a list of the dropped files (as a string)
        files = event.data.split()

        for file in files:
            # Handle each dropped file
            print(f"Dropped file: {file}")
            with open(file, "r", encoding="utf-8") as import_file:
                self._import_fields(import_file)
            break

    @property
    def _selected_number_of_bits(self):
        return 2 ** (BIT_LENGTHS.index(self.bit_length_string.get()) + 3)

    @staticmethod
    def _get_dropdown_index(bits: int) -> int:
        return int(log(bits) / log(2) - 3)

    def _bit_selection_clicked(self, _):
        self.register.bit_length = self._selected_number_of_bits
        self.swap_button.configure(
            state="disabled" if self.register.bit_length == 8 else "enabled"
        )
        self._update_bit_button()
        self.register.notify_observers()

    def _swap_bytes_button_click(self):
        self.register.swap_bytes()
        self.register.notify_observers()

    def _bit_order_button_click(self):
        self.register.bit_0_is_lsb = not self.register.bit_0_is_lsb
        self._update_bit_button()
        self.register.notify_observers()
        self.bin_entry.notify_observers()

    def _update_bit_button(self):
        new_button_label = (
            f"Swap numbering ({self.register.bit_length-1}:0)"
            if self.register.bit_0_is_lsb
            else f"Swap numbering (0:{self.register.bit_length-1})"
        )
        self.bin_numbering.config(text=self._get_numbering_label())
        self.bit_button.config(text=new_button_label)

    def _get_numbering_label(self) -> str:
        label = ""
        if self.register.bit_length == 8:
            if self.register.bit_0_is_lsb:
                label = "                              7       0"
            else:
                label = "                              0       7"
        elif self.register.bit_length == 16:
            if self.register.bit_0_is_lsb:
                label = "                    15      8|7       0"
            else:
                label = "                    0       7|8      15"
        elif self.register.bit_length == 32:
            if self.register.bit_0_is_lsb:
                label = "31     24|23     16|15      8|7       0"
            else:
                label = "0       7|8      15|16     23|24     31"

        return label

    def _show_menu(self, event):
        try:
            self.menu.post(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def _export_dialog(self):
        if (
            export_file := filedialog.asksaveasfile(
                defaultextension=".json",
                filetypes=[("JSON-files", "*.json"), ("All files", "*.*")],
            )
        ) is not None:
            self._export_fields(export_file)
            export_file.close()
            self.root.title(f"{self.window_title} - {Path(export_file.name).stem}")

    def _export_fields(self, file):
        export_fields = []
        for field in self.fields:
            export_fields.append(field.settings)

        export_data = {
            "bit length": self.register.bit_length,
            "bit 0 is lsb": self.register.bit_0_is_lsb,
            "fields": export_fields,
        }
        file.write(json.dumps(export_data, indent=4))

    def _import_dialog(self):
        if (
            import_file := filedialog.askopenfile(
                filetypes=[("JSON-files", "*.json"), ("All files", "*.*")]
            )
        ) is not None:
            self._import_fields(import_file)
            import_file.close()

    def _import_fields(self, file):
        self._reset_fields()
        import_data = json.loads(file.read())
        self.root.title(f"{self.window_title} - {Path(file.name).stem}")
        self.bit_length_string.set(
            BIT_LENGTHS[self._get_dropdown_index(import_data["bit length"])]
        )
        self.register.bit_0_is_lsb = import_data["bit 0 is lsb"]
        self._bit_selection_clicked(None)
        for field in import_data["fields"]:
            self._add_field(field["start"], field["end"], field["name"])

    def _sort_fields(self):
        sorted_fields = [field.settings for field in self.fields]
        sorted_fields.sort(
            key=lambda sorted_fields: sorted_fields["start"],
            reverse=self.register.bit_0_is_lsb,
        )

        self._reset_fields()
        for field in sorted_fields:
            self._add_field(field["start"], field["end"], field["name"])

    def _add_field_button_click(self):
        start_bit, end_bit = self.bin_entry.get_selection()
        if start_bit is not None and end_bit is not None:
            self._add_field(start_bit, end_bit)
            self.bin_entry.selection_clear()
            self.bin_entry.notify_observers()

    def _add_field(self, start_bit: int, end_bit: int, name=""):
        # If no previous fields, add labels first
        if len(self.fields) == 0:
            ttk.Label(self.bottomframe, text="Bits", borderwidth=5).grid(
                row=0, column=0, padx=1, pady=1
            )
            ttk.Label(self.bottomframe, text="Bin", borderwidth=5).grid(
                row=0, column=1, padx=1, pady=1, sticky="E"
            )
            ttk.Label(self.bottomframe, text="Hex", borderwidth=5).grid(
                row=0, column=2, padx=1, pady=1, sticky="E"
            )
            ttk.Label(self.bottomframe, text="Dec", borderwidth=5).grid(
                row=0, column=3, padx=1, pady=1, sticky="E"
            )
            ttk.Label(self.bottomframe, text="Name", borderwidth=5).grid(
                row=0, column=5, padx=3, pady=1, sticky="W"
            )

        # Create GUI for the field and place it on next available row
        next_row = len(self.fields) + 1
        gui_field = FieldGui(self.bottomframe, self.register, start_bit, end_bit, name)
        gui_field.grid(next_row)
        self.fields.append(gui_field)

    def _mouse_motion(self, _):
        self.bin_entry.notify_observers()

    def _on_expose(self, event):
        widget = event.widget
        if not widget.children:
            widget.configure(height=1)

    def _reset_fields(self):
        for field in self.fields:
            field.unregister()

        for widget in self.bottomframe.winfo_children():
            widget.destroy()

        self.fields.clear()

    def show(self):
        """Show the main window"""
        self.root.mainloop()

    def _show_about_popup(self):
        window = tk.Toplevel()
        window.wm_title("About")
        window.resizable(False, False)

        url = "https://github.com/fornstedt/registercalculator"

        header = tk.Label(window, text=f"RegisterCalculator version {VERSION}")
        link = tk.Label(window, text=url, fg="blue", cursor="hand2")
        author = tk.Label(window, text="Eric Fornstedt")

        link.bind("<Button-1>", lambda e: webbrowser.open_new(url))

        header.grid(row=0, column=0, padx=1, pady=1)
        link.grid(row=1, column=0, padx=5, pady=1)
        author.grid(row=2, column=0, padx=1, pady=1)
