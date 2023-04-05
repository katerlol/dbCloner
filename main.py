import customtkinter as ctk
from editServerPage import EditServerPage
from existingServerPage import ExistingServerPage
import Config

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")


class DBClonerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.new_server_button = None
        self.logo_label = None
        self.conf = Config.Config('db_cloner')

        self.geometry("800x890")
        self.title("Db Cloner")

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self.buttons = []

        # create sidebar frame with widgets

        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")

        # load server buttons for sidebar
        self.load_sidebar()

        # add container for page frames
        self.container = ctk.CTkFrame(self, corner_radius=0)
        self.container.grid(row=0, column=1, columnspan=2, padx=0, pady=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # add frames
        self.frames = {}

        for Page in (EditServerPage, ExistingServerPage):
            page_name = Page.__name__
            frame = Page(parent=self.container, controller=self, conf=self.conf)
            self.frames[page_name] = frame

            # put all frames in same location to be stacked
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame('EditServerPage', None)

        # add close listener to terminate app on close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_sidebar(self):
        for element in self.sidebar_frame.winfo_children():
            element.destroy()
        self.buttons = []

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="DB Cloner", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.new_server_button = ctk.CTkButton(self.sidebar_frame, text="Add server",
                                               command=lambda: self.show_frame('EditServerPage', None))
        self.new_server_button.grid(row=1, column=0, padx=20, pady=20)

        for i, server in enumerate(self.conf.data['servers']):
            existing_server_button = ctk.CTkButton(self.sidebar_frame, text=server['name'],
                                                   command=lambda s=server: self.show_frame('ExistingServerPage', s))
            existing_server_button.grid(row=(i + 2), column=0, padx=20, pady=5)
            self.buttons.append(existing_server_button)

    def add_server(self, server):
        self.conf.data['servers'].append(server)
        self.conf.save_data()
        self.load_sidebar()

    def update_server(self, server):
        for i, other in enumerate(self.conf.data["servers"]):
            if server["uuid"] == other["uuid"]:
                self.conf.data["servers"][i] = server
        self.conf.save_data()
        self.load_sidebar()

    def delete_server(self, server):

        for other in self.conf.data["servers"]:
            if server["uuid"] == other["uuid"]:
                self.conf.data['servers'].remove(other)
        self.conf.save_data()
        self.load_sidebar()

    def show_frame(self, page_name, server):
        # display the proper frame
        frame = self.frames[page_name]
        if server is not None:
            frame.fill(server)
        else:
            frame.clear()
        frame.tkraise()

    def on_closing(self):
        print("Good bye!")
        self.destroy()


if __name__ == '__main__':
    App = DBClonerGUI()
    App.mainloop()
