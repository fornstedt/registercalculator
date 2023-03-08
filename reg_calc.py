import tkinter as tk
from tkinter import ttk, END


class RegCalcWindow:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.rowconfigure(0, minsize=20)
        self.root.rowconfigure(1, minsize=30)

        self.hex_label = ttk.Label(text="Hex", borderwidth=5).grid(row=0, column=0)
        self.dec_label = ttk.Label(text="Dec", borderwidth=5).grid(row=0, column=2)

        self.hex_entry = ttk.Entry(width=8, justify='right')
        self.hex_entry.bind('<Any-KeyRelease>', self.hex_keyrelease)
        self.hex_entry.grid(row=0, column=1)

        self.dec_entry = ttk.Entry(width=8, justify='right')
        self.dec_entry.bind('<Any-KeyRelease>', self.dec_keyrelease)
        self.dec_entry.grid(row=0, column=3)

        self.bin_entry = ttk.Entry(width=39)
        self.bin_entry.grid(row=1, column=0, columnspan=4)

    def hex_keyrelease(self, event):
        value = self.hex_entry.get()
        dec_value = self.get_dec_string(value)
        self.set_text(self.hex_entry, value.upper())
        self.set_text(self.dec_entry, dec_value)
        self.set_text(self.bin_entry, self.get_bin_string(dec_value))

    def dec_keyrelease(self, event):
        value = self.dec_entry.get()
        self.set_text(self.hex_entry, self.get_hex_string(value))
        self.set_text(self.bin_entry, self.get_bin_string(value))

    @staticmethod
    def get_hex_string(value: str) -> str:
        try:
            hex_value = f'{int(value):X}'
        except ValueError:
            hex_value = 'Error'

        return hex_value

    @staticmethod
    def get_dec_string(value: str) -> str:
        try:
            dec_value = f'{int(value, 16)}'
        except ValueError:
            dec_value = 'Error'

        return dec_value

    @staticmethod
    def get_bin_string(value: str) -> str:
        try:
            bin_value = f'{int(value):032b}'
        except ValueError:
            bin_value = 'Error'

        return bin_value

    @staticmethod
    def set_text(entry, text):
        entry.delete(0, END)
        entry.insert(0, text)

    def show(self):
        self.root.mainloop()


def main():
    reg_calc_window = RegCalcWindow()
    reg_calc_window.show()


if __name__ == "__main__":
    main()
