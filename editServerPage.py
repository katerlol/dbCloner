import customtkinter as ctk
import uuid
import custom_widgets.widget_helper as wh
from custom_widgets.server_name import ServerName
from custom_widgets.mysql_server_input import MySQLServerInput


class EditServerPage(ctk.CTkFrame):

    def __init__(self, parent, controller, conf):
        ctk.CTkFrame.__init__(self, parent)
        self.controller = controller

        self.server = None

        self.grid_columnconfigure(4, weight=1)

        self.page_title = ctk.CTkLabel(self, font=ctk.CTkFont(size=20, weight="bold"), anchor="w")
        self.page_title.grid(row=1, column=0, padx=10, pady=10, columnspan=2)

        self.server_name = ServerName(self, controller, "General")
        self.server_name.grid(row=3, column=0, columnspan=2, padx=10, pady=(5, 10))

        self.source_server = MySQLServerInput(self, controller, "Source")
        self.source_server.grid(row=5, column=0, columnspan=2, padx=10, pady=(5, 10))

        self.dest_server = MySQLServerInput(self, controller, "Destination")
        self.dest_server.grid(row=7, column=0, columnspan=2, padx=10, pady=(5, 10))

        self.delete_button = ctk.CTkButton(self, text="Delete", width=250,
                                           command=lambda: wh.confirm("Delete server",
                                                                      "Do you really want to delete this server?",
                                                                      self.delete_server))
        self.delete_button.grid(row=8, column=0, pady=10, padx=5)

        self.save_button = ctk.CTkButton(self, text="Save", command=self.save_server)
        self.save_button.grid(row=8, column=1, pady=10, padx=5)

        self.clear()

    def clear(self):
        self.page_title.configure(text="Add server")
        self.save_button.configure(width=530)
        self.save_button.grid(column=0)
        self.delete_button.grid_forget()
        self.server_name.clear()
        self.source_server.clear()
        self.dest_server.clear()
        self.server = None

    def fill(self, server):
        self.page_title.configure(text="Edit server")
        self.delete_button.grid(row=8, column=0)
        self.save_button.grid(row=8, column=1)
        self.save_button.configure(width=250)
        self.server_name.fill(server["name"])
        self.source_server.fill(server["source"])
        self.dest_server.fill(server["destination"])
        self.server = server

    def save_server(self):
        is_new = self.server is None
        if is_new:
            self.server = {
                "uuid": str(uuid.uuid1()),
            }

        self.server["name"] = self.server_name.get()
        self.server["source"] = self.source_server.get()
        self.server["destination"] = self.dest_server.get()

        if is_new:
            self.controller.add_server(server=self.server)
            self.clear()
        else:
            self.controller.update_server(server=self.server)

    def delete_server(self):
        self.controller.delete_server(server=self.server)
        self.clear()
