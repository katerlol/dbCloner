import customtkinter as ctk

from clonePage import ClonePage
from editServerPage import EditServerPage


class ExistingServerPage(ctk.CTkFrame):

    def __init__(self, parent, controller, conf):
        ctk.CTkFrame.__init__(self, parent)
        self.controller = controller

        # create tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=2, padx=5, pady=0, sticky="nsew")
        self.tabview.add("Backups")
        self.clonePage = ClonePage(parent=self.tabview.tab("Backups"), controller=controller, conf=conf)
        self.clonePage.grid(row=0, column=0, sticky="nsew")
        self.tabview.tab("Backups").grid_columnconfigure(0, weight=1)

        self.tabview.add("Settings")
        self.editServerPage = EditServerPage(parent=self.tabview.tab("Settings"), controller=controller, conf=conf)
        self.editServerPage.grid(row=0, column=0, sticky="nsew")
        self.tabview.tab("Settings").grid_columnconfigure(0, weight=1)

    def fill(self, server):
        self.clonePage.fill(server)
        self.editServerPage.fill(server)
