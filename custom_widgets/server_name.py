import customtkinter as ctk
import custom_widgets.widget_helper as wh


class ServerName(ctk.CTkFrame):

    def __init__(self, parent, controller, name):
        ctk.CTkFrame.__init__(self, parent)

        self.controller = controller

        self.server_name = ctk.StringVar(self, '')

        self.server_title = wh.add_h2(self, name, 2, 2)
        self.server_name_label, self.server_name_input = wh.add_entry(self, "Server name", "e.g. prod server",
                                                                      self.server_name, 3)

    def fill(self, server_name):
        self.server_name.set(server_name)

    def clear(self):
        self.server_name.set("")

    def get(self):
        return self.server_name.get()
