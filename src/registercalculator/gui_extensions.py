"""Module which extends ttk entries with hex/dec/bin functionality"""

from string import hexdigits
from tkinter import END, INSERT, Frame, ttk, IntVar
from typing import Union

from registercalculator.register import DELIMITER, DataField, DataRegister

NAME_FIELD_WIDTH = 30


class HexEntry(ttk.Entry):
    """A ttk Entry that accepts only hexadecimal values and is connected to a register"""

    def __init__(self, frame: Frame, field: Union[DataRegister, DataField]):
        self._frame = frame
        self._field = field
        super().__init__(
            frame,
            width=self._field.max_hex_width,
            justify="right",
            font="TkFixedFont",
            validate="key",
            validatecommand=(frame.register(self._validate), "%S", "%P"),
        )
        self.bind("<Any-KeyRelease>", self._key_release)
        self._field.register_observer(self._observer_callback)

    def _validate(self, text_to_insert: str, all_text: str) -> bool:
        if not all(c in hexdigits for c in text_to_insert):
            return False
        if not len(all_text) <= self._field.max_hex_width:
            return False
        if not ((all_text == "") or (int(all_text, 16) <= self._field.max)):
            return False
        return True

    def _key_release(self, _):
        value_string = self.get()
        self._field.value = int(value_string, 16) if value_string != "" else 0

    def _observer_callback(self):
        index = self.index(INSERT)
        self.config(state="enabled")
        self.delete(0, END)
        try:
            self.insert(0, self._field.hex)
            self.config(state="enabled")
        except ValueError:
            self.insert(0, "0")
            self.config(state="disabled")
        self.icursor(index)

    def unregister(self):
        """Unregister the entry from register changes"""
        self._field.unregister_observer(self._observer_callback)


class DecEntry(ttk.Entry):
    """A ttk Entry that accepts only decimal values and is connected to a register"""

    def __init__(self, frame: Frame, field: Union[DataRegister, DataField]):
        self._frame = frame
        self._field = field
        super().__init__(
            frame,
            width=self._field.max_dec_width,
            justify="right",
            font="TkFixedFont",
            validate="key",
            validatecommand=(frame.register(self._validate), "%S", "%P"),
        )
        self.bind("<Any-KeyRelease>", self._key_release)
        self._field.register_observer(self._observer_callback)

    def _validate(self, text_to_insert: str, all_text: str) -> bool:
        if not text_to_insert.isdecimal():
            return False
        if not len(all_text) <= self._field.max_dec_width:
            return False
        if not ((all_text == "") or (int(all_text) <= self._field.max)):
            return False
        return True

    def _key_release(self, _):
        value_string = self.get()
        self._field.value = int(value_string) if value_string != "" else 0

    def _observer_callback(self):
        index = self.index(INSERT)
        self.config(state="enabled")
        self.delete(0, END)
        try:
            self.insert(0, self._field.dec)
            self.config(state="enabled")
        except ValueError:
            self.insert(0, "0")
            self.config(state="disabled")
        self.icursor(index)

    def unregister(self):
        """Unregister the entry from register changes"""
        self._field.unregister_observer(self._observer_callback)


class BinEntry(ttk.Entry):
    """A ttk Entry that accepts only binary values and is connected to a register"""

    def __init__(
        self, frame: Frame, field: Union[DataRegister, DataField], with_delimiter=False
    ):
        self._with_delimiter = with_delimiter
        self._frame = frame
        self._field = field
        width = self._field.bit_length

        if self._with_delimiter:
            width += self._field.bit_length // 4 - 1

        super().__init__(
            frame,
            width=width,
            justify="right",
            font="TkFixedFont",
            validate="key",
            validatecommand=(frame.register(self._validate), "%S", "%P"),
        )
        self.bind("<Any-KeyRelease>", self._key_release)
        self._field.register_observer(self._observer_callback)

    def _validate(self, text_to_insert: str, all_text: str) -> bool:
        allowed_characters = "01"
        allowed_length = self._field.bit_length

        if self._with_delimiter:
            allowed_characters += DELIMITER
            allowed_length += self._field.bit_length // 4 - 1

        if not all(c in allowed_characters for c in text_to_insert):
            return False
        if not len(all_text) <= allowed_length:
            return False
        return True

    def _key_release(self, _):
        value_string = self.get()
        self._field.value = int(value_string, 2) if value_string != "" else 0

    def _observer_callback(self):
        index = self.index(INSERT)
        self.config(state="enabled")
        self.delete(0, END)
        try:
            self.insert(
                0,
                self._field.bin_delimited if self._with_delimiter else self._field.bin,
            )
            self.config(state="enabled")
        except ValueError:
            self.insert(0, "0")
            self.config(state="disabled")
        self.icursor(index)

    def unregister(self):
        """Unregister the entry from register changes"""
        self._field.unregister_observer(self._observer_callback)


class FieldGui(DataField):
    """A ttk gui object that represent a register field on a row"""

    def __init__(
        self,
        frame: Frame,
        register: DataRegister,
        start_bit: int,
        end_bit: int,
        name: str = "",
    ) -> None:
        super().__init__(register, start_bit, end_bit)

        self.bit_label = ttk.Label(frame, borderwidth=5)
        self.bin_entry = BinEntry(frame, self)
        self.hex_entry = HexEntry(frame, self)
        self.dec_entry = DecEntry(frame, self)

        self.checkbox_value = IntVar()
        self.checkbox = None
        if end_bit - start_bit == 0:  # bit length 1
            self.checkbox = ttk.Checkbutton(
                frame, variable=self.checkbox_value, command=self._toggle_value
            )
            self.checkbox_value.set(self.value)

        self.name_entry = ttk.Entry(
            frame, width=NAME_FIELD_WIDTH, justify="left", font="TkFixedFont"
        )
        self.name_entry.bind("<Any-KeyRelease>", self._name_field_keyrelease)

        self.name_entry.insert(0, name)
        self._adjust_entry_length()

    def grid(self, row):
        """Position the widget in the parent at a specific row"""
        self.bit_label.grid(row=row, column=0, padx=1, pady=1)
        self.bin_entry.grid(row=row, column=1, sticky="E", padx=3, pady=1)
        self.hex_entry.grid(row=row, column=2, sticky="E", padx=3, pady=1)
        self.dec_entry.grid(row=row, column=3, sticky="E", padx=3, pady=1)
        if self.checkbox is not None:
            self.checkbox.grid(row=row, column=4, sticky="E", padx=3, pady=1)
        self.name_entry.grid(
            row=row, column=5, sticky="W", padx=3, pady=1, columnspan=2
        )
        self.register_observer(self._observer_callback)
        self._register.notify_observers()

    def _toggle_value(self):
        """Toggle the value of the field between 1 and 0"""
        self.value = self.checkbox_value.get()

    def _update_checkbox(self):
        """Update the checkbox value based on the field value"""
        if self.checkbox is not None:
            self.checkbox_value.set(self.value)

    def _name_field_keyrelease(self, _):
        self._adjust_entry_length()

    def _adjust_entry_length(self, minimum=NAME_FIELD_WIDTH):
        length = len(self.name_entry.get())
        if length > minimum:
            self.name_entry.configure(width=length)

    @property
    def settings(self) -> dict:
        """Dict containing the field's settings"""
        settings = {
            "name": self.name_entry.get(),
            "start": self.start_bit,
            "end": self.end_bit,
        }
        return settings

    def unregister(self):
        """Unregister the widget from register changes"""
        self.hex_entry.unregister()
        self.dec_entry.unregister()
        self.bin_entry.unregister()
        self.unregister_observer(self._observer_callback)

    def _observer_callback(self):
        if self.start_bit >= 0 and self.end_bit >= 0:
            self._update_checkbox()
            self.bit_label.config(text=f"{self.start_bit}:{self.end_bit}")
        else:
            self.bit_label.config(text="N/A")
