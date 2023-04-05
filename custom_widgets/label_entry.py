import customtkinter as ctk
import custom_widgets.widget_helper as wh


class LabelEntry(ctk.CTkFrame):

    def __init__(self, parent, controller, name, var, entry_type="entry"):
        ctk.CTkFrame.__init__(self, parent)

        self.controller = controller

        label = ctk.CTkLabel(s, text=name, width=200, anchor="e")
        label.grid(row=0, column=0, pady=(0, 5), padx=5)
        entry = ctk.CTkEntry(parent, textvariable=var, width=300)

        if "password" == entry_type:
            entry.configure(show="•")

        entry.grid(row=0, column=1, columnspan=2, pady=(0, 5), padx=5)
        entry.delete(0, ctk.END)
