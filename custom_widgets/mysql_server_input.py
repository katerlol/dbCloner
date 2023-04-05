import customtkinter as ctk
import custom_widgets.widget_helper as wh
import mysql_manager


class MySQLServerInput(ctk.CTkFrame):

    def __init__(self, parent, controller, name):
        ctk.CTkFrame.__init__(self, parent)

        self.controller = controller

        self.server_type = ctk.StringVar(self, '')

        self.ssh_host = ctk.StringVar(self, '')
        self.ssh_port = ctk.IntVar(self, 22)
        self.ssh_user = ctk.StringVar(self, '')
        self.ssh_passwd = ctk.StringVar(self, '')
        self.ssh_auth_method = ctk.StringVar(self, '')
        self.ssh_auth_value = ctk.StringVar(self, '')

        self.host = ctk.StringVar(self, '')
        self.port = ctk.IntVar(self, 3306)
        self.user = ctk.StringVar(self, '')
        self.passwd = ctk.StringVar(self, '')
        self.db = ctk.StringVar(self, '')
        self.override_db = ctk.BooleanVar(self, True)

        self.title = wh.add_h2(self, name, 0, 1)
        self.type = wh.add_option_menu(self, [
            "Choose a type",
            "Standard (TCP/IP)",
            "TCP/IP over SSH",
        ], 0, self.on_change)

        self.ssh_host_label, self.ssh_host_input, self.ssh_port_input \
            = wh.add_host_port_entry(self, "SSH Host | Port", self.ssh_host, self.ssh_port, 1)
        self.ssh_user_label, self.ssh_user_input = wh.add_entry(self, "SSH User", "e.g. ssh_user", self.ssh_user, 2)
        self.ssh_method_label, self.ssh_auth_method_options, self.ssh_auth_value_input = \
            wh.add_option_entry(self, "SSH Method", self.ssh_auth_value, 3,
                                lambda value: self.ssh_auth_method.set(value))
        self.host_label, self.host_input, self.port_input = \
            wh.add_host_port_entry(self, "Host | Port", self.host, self.port, 5)
        self.user_label, self.user_input = wh.add_entry(self, "User", "e.g. db_user", self.user, 6)
        self.pass_label, self.pass_input = wh.add_entry(self, "Password", "••••••••", self.passwd, 7, "password")
        self.db_label, self.db_input, self.db_override_checkbox = wh.add_checkbox_entry(
            self, "Database", "database_live", "override", self.db, self.override_db, 8)

        self.connection_test_label = ctk.CTkLabel(self, text="", width=100)
        self.connection_test_button = ctk.CTkButton(self, text="Test connection", width=200,
                                                    command=self.test_connection)

        self.on_change("Choose a type")

    def fill(self, server):
        self.connection_test_label.configure(text="")
        self.ssh_host.set(server["ssh_host"])
        self.ssh_port.set(int(server["ssh_port"]))
        self.ssh_user.set(server["ssh_user"])
        self.ssh_auth_value.set(server["ssh_auth_value"])
        self.ssh_auth_method.set(server["ssh_auth_method"])

        self.host.set(server["host"])
        self.port.set(int(server["port"]))
        self.user.set(server["user"])
        self.passwd.set(server["passwd"])
        self.db.set(server["db"])

        self.type.set(server["server_type"])
        self.on_change(server["server_type"])

    def clear(self):
        self.connection_test_label.configure(text="")
        self.ssh_host.set("")
        self.ssh_port.set(22)
        self.ssh_user.set("")
        self.ssh_auth_value.set("")
        self.ssh_auth_method.set("Password")

        self.host.set("")
        self.port.set(3306)
        self.user.set("")
        self.passwd.set("")
        self.db.set("")

        self.type.set("Choose a type")
        self.on_change("Choose a type")

    def get(self):
        return {
            "server_type": self.server_type.get(),

            "ssh_host": self.ssh_host.get(),
            "ssh_port": self.ssh_port.get(),
            "ssh_user": self.ssh_user.get(),
            "ssh_auth_method": self.ssh_auth_method.get(),
            "ssh_auth_value": self.ssh_auth_value.get(),

            "host": self.host.get(),
            "port": self.port.get(),
            "user": self.user.get(),
            "passwd": self.passwd.get(),
            "db": self.db.get(),
        }

    def test_connection(self):
        self.connection_test_label.configure(text="")

        connection_result = mysql_manager.test_connection(self.get())

        if not connection_result["success"]:
            wh.show_error("Database connection error", connection_result["error"])
            self.connection_test_label.configure(text="Error")
        else:
            wh.show_info("Database connection successful", connection_result["message"])
            self.connection_test_label.configure(text="Success")

    def enable_ssh(self):
        self.ssh_host_label.grid(row=1, column=0, pady=(0, 5), padx=5)
        self.ssh_user_label.grid(row=2, column=0, pady=(0, 5), padx=5)
        self.ssh_method_label.grid(row=3, column=0,  pady=(0, 5), padx=5)
        self.ssh_host_input.grid(row=1, column=1, columnspan=2, pady=(0, 5), padx=(5, 5))
        self.ssh_port_input.grid(row=1, column=3, columnspan=1, pady=(0, 5), padx=(0, 5))
        self.ssh_user_input.grid(row=2, column=1, columnspan=3, pady=(0, 5), padx=5)
        self.ssh_auth_method_options.grid(row=3, column=1, pady=(0, 15), padx=(5, 0))
        self.ssh_auth_value_input.grid(row=3, column=2, columnspan=2, pady=(0, 15), padx=5)

    def disable_ssh(self):
        self.ssh_host_label.grid_forget()
        self.ssh_host_input.grid_forget()
        self.ssh_port_input.grid_forget()
        self.ssh_user_label.grid_forget()
        self.ssh_user_input.grid_forget()
        self.ssh_method_label.grid_forget()
        self.ssh_auth_method_options.grid_forget()
        self.ssh_auth_value_input.grid_forget()

    def enable_connection_test_button(self):
        self.connection_test_label.grid(row=9, column=1, padx=(5, 0), pady=(0, 5))
        self.connection_test_button.grid(row=9, column=2, columnspan=2, padx=(0, 5), pady=(0, 5))

    def disable_connection_test_button(self):
        self.connection_test_button.grid_forget()
        self.connection_test_label.grid_forget()

    def enable_mysql(self):
        self.host_label.grid(row=4, column=0, pady=(0, 5), padx=5)
        self.user_label.grid(row=5, column=0, pady=(0, 5), padx=5)
        self.pass_label.grid(row=6, column=0, pady=(0, 5), padx=5)
        self.db_label.grid(row=7, column=0, pady=(0, 5), padx=5)
        self.host_input.grid(row=4, column=1, columnspan=2, pady=(0, 5), padx=(5, 5))
        self.port_input.grid(row=4, column=3, columnspan=1, pady=(0, 5), padx=(0, 5))
        self.user_input.grid(row=5, column=1, columnspan=3, pady=(0, 5), padx=5)
        self.pass_input.grid(row=6, column=1, columnspan=3, pady=(0, 5), padx=5)
        self.db_input.grid(row=7, column=1, columnspan=2, pady=(0, 5), padx=5)
        self.db_override_checkbox.grid(row=7, column=3, columnspan=3, pady=(0, 5), padx=(0, 5))

    def disable_mysql(self):
        self.host_label.grid_forget()
        self.user_label.grid_forget()
        self.pass_label.grid_forget()
        self.db_label.grid_forget()
        self.host_input.grid_forget()
        self.port_input.grid_forget()
        self.user_input.grid_forget()
        self.pass_input.grid_forget()
        self.db_input.grid_forget()
        self.db_override_checkbox.grid_forget()

    def on_change(self, new_value):
        self.server_type.set(new_value)

        if new_value == "Standard (TCP/IP)":
            self.disable_ssh()
            self.enable_mysql()
            self.enable_connection_test_button()

        elif new_value == "Choose a type":
            self.disable_ssh()
            self.disable_mysql()
            self.disable_mysql()
            self.disable_connection_test_button()

        elif new_value == "TCP/IP over SSH":
            self.enable_ssh()
            self.enable_mysql()
            self.enable_connection_test_button()
