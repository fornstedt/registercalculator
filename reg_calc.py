import tkinter as tk
from tkinter import ttk, END, INSERT
from string import hexdigits
from contextlib import suppress


class RegCalcWindow:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.rowconfigure(0, minsize=20)
        self.root.rowconfigure(1, minsize=30)
        self.root.title('Register Calculator')

        self.hex_label = ttk.Label(text="Hex", borderwidth=5).grid(row=0, column=0)
        self.dec_label = ttk.Label(text="Dec", borderwidth=5).grid(row=0, column=2)

        self.hex_entry = ttk.Entry(width=8, justify='right', font='TkFixedFont', validate='key',
                                   validatecommand=(self.root.register(self.is_hex), "%S", "%P"))
        self.dec_entry = ttk.Entry(width=10, justify='right', font='TkFixedFont', validate='key',
                                   validatecommand=(self.root.register(self.is_decimal), "%S", "%P"))
        self.bin_entry = ttk.Entry(width=39, justify='right', font='TkFixedFont', validate='key',
                                   validatecommand=(self.root.register(self.is_bin), "%S", "%P"))
             
        self.hex_entry.bind('<Any-KeyRelease>', self.hex_keyrelease)
        self.dec_entry.bind('<Any-KeyRelease>', self.dec_keyrelease)
        self.bin_entry.bind('<Any-KeyRelease>', self.bin_keyrelease)
        
        self.hex_entry.grid(row=0, column=1)
        self.dec_entry.grid(row=0, column=3)
        self.bin_entry.grid(row=1, column=0, columnspan=4)

    @staticmethod
    def is_decimal(text_to_insert, all_text):
        return text_to_insert.isdecimal() and (all_text == '' or (int(all_text) <= 0xFFFFFFFF))
    
    @staticmethod
    def is_hex(text_to_insert, all_text):
        return len(all_text) <= 8 and all(c in hexdigits for c in text_to_insert)
    
    @staticmethod
    def is_bin(text_to_insert, all_text):
        return len(all_text) <= 32 and all(c in '01' for c in text_to_insert)

    def hex_keyrelease(self, event):
        value = self.hex_entry.get()
        dec_value = self.hex_to_dec(value)
        self.set_text(self.dec_entry, dec_value)
        self.set_text(self.bin_entry, self.dec_to_bin(dec_value))

    def dec_keyrelease(self, event):
        value = self.dec_entry.get()
        self.set_text(self.hex_entry, self.dec_to_hex(value))
        self.set_text(self.bin_entry, self.dec_to_bin(value))
        
    def bin_keyrelease(self, event):
        print(self.bin_entry.index(INSERT))
        value = self.bin_entry.get()
        dec_value = self.bin_to_dec(value)
        self.set_text(self.hex_entry, self.dec_to_hex(dec_value))
        self.set_text(self.dec_entry, dec_value)

    @staticmethod
    def dec_to_hex(value: str) -> str:
        with suppress(ValueError): hex_value = f'{int(value):X}'
        return hex_value

    @staticmethod
    def hex_to_dec(value: str) -> str:
        with suppress(ValueError): dec_value = f'{int(value, 16)}'
        return dec_value

    @staticmethod
    def dec_to_bin(value: str) -> str:
        with suppress(ValueError): bin_value = f'{int(value):032b}'
        return bin_value
    
    @staticmethod
    def bin_to_dec(value: str) -> str:
        with suppress(ValueError): dec_value = f'{int(value, 2)}'
        return dec_value

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
