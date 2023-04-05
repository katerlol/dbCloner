import customtkinter as ctk
from tkinter import messagebox


def confirm(title, message, confirmed_method):
    msg_box = messagebox.askquestion(title, message, icon='warning')
    if "yes" == msg_box:
        confirmed_method()


def show_error(title, message):
    messagebox.showerror(title, message)


def show_info(title, message):
    messagebox.showinfo(title, message)


def add_h2(parent, name, row, colspan=2):
    h2 = ctk.CTkLabel(parent, text=name, font=ctk.CTkFont(size=16, weight="bold"), anchor="e", width=200)
    h2.grid(row=row, column=0, columnspan=colspan, padx=10, pady=(5, 5))
    return h2


def add_entry(parent, name, description, var, row, entry_type="entry"):
    label = ctk.CTkLabel(parent, text=name, width=200, anchor="e")
    label.grid(row=row, column=0, pady=(0, 5), padx=5)
    entry = ctk.CTkEntry(parent, placeholder_text=description, textvariable=var, width=300)

    if "password" == entry_type:
        entry.configure(show="•")

    entry.grid(row=row, column=1, columnspan=3, pady=(0, 5), padx=5)
    entry.delete(0, ctk.END)
    return label, entry


def add_checkbox_entry(parent, name, description, checkbox_name, entry_var, checkbox_var, row):
    label = ctk.CTkLabel(parent, text=name, width=200, anchor="e")
    label.grid(row=row, column=0, pady=(0, 5), padx=5)
    entry = ctk.CTkEntry(parent, placeholder_text=description, textvariable=entry_var, width=200)
    entry.grid(row=row, column=1, columnspan=2, pady=(0, 5), padx=5)
    checkbox = ctk.CTkCheckBox(parent, variable=checkbox_var, width=95, text=checkbox_name)
    checkbox.grid(row=row, column=3, pady=(0, 5), padx=(0, 5))
    return label, entry, checkbox


def add_host_port_entry(parent, name, host_var, host_port, row):
    label = ctk.CTkLabel(parent, text=name, width=200, anchor="e")
    label.grid(row=row, column=0, pady=(0, 5), padx=5)
    host_entry = ctk.CTkEntry(parent, placeholder_text="e.g. 127.0.0.1", textvariable=host_var, width=200)
    host_entry.grid(row=row, column=1, columnspan=2, pady=(5, 5), padx=5)
    port_entry = ctk.CTkEntry(parent, placeholder_text="e.g. 3306", textvariable=host_port, width=95)
    port_entry.grid(row=row, column=3, columnspan=1, pady=(0, 5), padx=5)

    return label, host_entry, port_entry


def add_option_entry(parent, name, var, row, callback):
    label = ctk.CTkLabel(parent, text=name, width=200, anchor="e")
    label.grid(row=row, column=0, pady=(0, 5), padx=5)
    option_menu = ctk.CTkOptionMenu(parent, values=['Password', 'Keyfile'], width=100, command=callback, anchor="n")
    option_menu.grid(row=row, column=1, pady=0, padx=(5, 0))
    entry = ctk.CTkEntry(parent, textvariable=var, width=195)
    entry.grid(row=row, column=2, columnspan=2, pady=0, padx=(0, 5))
    return label, option_menu, entry


def add_option_menu(parent, options, row, callback):
    option_menu = ctk.CTkOptionMenu(parent, values=options, width=300, command=callback)
    option_menu.grid(row=row, column=1, columnspan=3, pady=(5, 5), padx=5)

    return option_menu
