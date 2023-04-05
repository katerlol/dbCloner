import customtkinter as ctk
import time
import mysql_manager
import custom_widgets.widget_helper as wh


class ClonePage(ctk.CTkFrame):

    def __init__(self, parent, controller, conf):
        ctk.CTkFrame.__init__(self, parent)
        self.controller = controller
        self.server = None
        self.tunnel = None
        self.start = None
        self.conf = conf

        self.page_title = ctk.CTkLabel(self, font=ctk.CTkFont(size=20, weight="bold"), anchor="w")
        self.page_title.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        self.backup_state_frame = ctk.CTkFrame(self, corner_radius=0)
        self.backup_state_frame.grid(row=1, column=1, pady=10, padx=15, sticky="ew")
        self.backup_state_title = ctk.CTkLabel(self.backup_state_frame, text="Backup status",
                                               font=ctk.CTkFont(size=20, weight="bold"), width=490)
        self.backup_state_title.grid(row=1, column=1, pady=(15, 5), padx=15, sticky="ew")

        self.backup_status_label = ctk.CTkLabel(self.backup_state_frame, text="Click to start a backup")
        self.backup_status_label.grid(row=2, column=1, pady=5, padx=15, sticky="ew")

        self.backup_process_bar = ctk.CTkProgressBar(self.backup_state_frame)
        self.backup_process_bar.grid(row=3, column=1, pady=5, padx=15, sticky="ew")
        self.backup_process_bar.configure(mode="determinate", indeterminate_speed=1.5)
        self.backup_process_bar.set(1.)

        self.snapshot_button = ctk.CTkButton(self, text="Take snapshot of source",
                                             command=lambda: self.take_snapshot(self.server["source"]), width=520)
        self.snapshot_button.grid(row=2, column=1, pady=5, padx=15)

        self.snapshot_button_destination = ctk.CTkButton(self, text="Take snapshot of destination",
                                                         command=lambda: self.take_snapshot(self.server["destination"]),
                                                         width=520)
        self.snapshot_button_destination.grid(row=3, column=1, pady=5, padx=15)

        self.source_to_dest_button = ctk.CTkButton(self, command=self.copy_source_to_destination, width=520)
        self.source_to_dest_button.configure(text="Copy source to destination")
        self.source_to_dest_button.grid(row=4, column=1, pady=5, padx=15)

        self.restore_last_backup = ctk.CTkButton(self, command=self.on_start_restore, width=520)
        self.restore_last_backup.configure(text="Restore last backup")
        self.restore_last_backup.grid(row=5, column=1, pady=5, padx=15)

    def fill(self, server):
        self.server = server
        self.page_title.configure(text=server["name"])

    def set_button_state(self, value):
        self.snapshot_button.configure(state=value)
        self.snapshot_button_destination.configure(state=value)
        self.source_to_dest_button.configure(state=value)
        self.restore_last_backup.configure(state=value)

    def on_backup_finished(self):
        end = time.perf_counter()

        # UI updates
        self.backup_status_label.configure(
            text=str(f"Backup created. Took {str(round(end - self.start, 2))} seconds."))
        self.set_button_state(ctk.NORMAL)
        self.backup_process_bar.configure(mode="determinate")
        self.backup_process_bar.stop()
        self.backup_process_bar.set(1.)

    def take_snapshot(self, server):
        error = mysql_manager.start_backup(server, "back.sql", self.conf, self.on_backup_finished)
        if error is not None:
            wh.show_error("Database connection error", error)
            return

        self.start = time.perf_counter()

        # UI updates
        self.set_button_state(ctk.DISABLED)
        self.backup_status_label.configure(text="Backup in progress. Don't close the program.")
        self.backup_process_bar.configure(mode="indeterminate")
        self.backup_process_bar.start()

        print(f"taking snapshot of {self.server['name']}")

    def copy_source_to_destination(self):
        print(f"taking apply_source_to_destination of {self.server['name']}")
        self.start = time.perf_counter()
        if mysql_manager.db_exists(self.server["destination"], self.server["destination"]["db"]):
            wh.confirm("The destination database already exists.",
                       "Do you really want to override the current destination database '"
                       + self.server["destination"]["db"] + "'? This action cannot be undone.",
                       self.copy_source_to_destination_confirmed)
        else:
            self.copy_source_to_destination_confirmed()

    def copy_source_to_destination_confirmed(self):
        mysql_manager.delete_db_if_exists(self.server["destination"], self.server["destination"]["db"])
        mysql_manager.create_db_if_not_exists(self.server["destination"], self.server["destination"]["db"])

        error = mysql_manager.start_backup(self.server["source"], f"{self.server['uuid']}.sql",
                                           self.conf, self.on_start_restore)
        if error is not None:
            wh.show_error("Database connection error", error)
            return

        # UI updates
        self.set_button_state(ctk.DISABLED)
        self.backup_status_label.configure(text="Backup in progress. Don't close the program.")
        self.backup_process_bar.configure(mode="indeterminate")
        self.backup_process_bar.start()

    def on_start_confirmed(self):
        mysql_manager.delete_db_if_exists(self.server["destination"], self.server["destination"]["db"])
        mysql_manager.create_db_if_not_exists(self.server["destination"], self.server["destination"]["db"])
        error = mysql_manager.start_restore(self.server["destination"], f"{self.server['uuid']}.sql",
                                            self.conf, self.on_restore_finished)

        if error is not None:
            wh.show_error("Database connection error", error)
            self.backup_status_label.configure(
                text=str("Error on restoration"))
            self.set_button_state(ctk.NORMAL)
            self.backup_process_bar.configure(mode="determinate")
            self.backup_process_bar.stop()
            self.backup_process_bar.set(1.)
            return

        # UI updates
        self.set_button_state(ctk.DISABLED)
        self.backup_status_label.configure(text="Restore in progress. Don't close the program.")
        self.backup_process_bar.configure(mode="indeterminate")
        self.backup_process_bar.start()

    def on_start_restore(self):
        if self.start is None:
            self.start = time.perf_counter()
            if mysql_manager.db_exists(self.server["destination"], self.server["destination"]["db"]):
                wh.confirm("The destination database already exists.",
                           f'Do you really want to override the current destination database '
                           f'\'{self.server["destination"]["db"]}\'? This action cannot be undone.',
                           self.on_start_confirmed)
        else:
            self.on_start_confirmed()

    def on_restore_finished(self):
        end = time.perf_counter()
        # UI updates
        self.backup_status_label.configure(
            text=str("Restore finished. Took " + str(round(end - self.start, 2)) + " seconds."))
        self.set_button_state(ctk.NORMAL)
        self.backup_process_bar.configure(mode="determinate")
        self.backup_process_bar.stop()
        self.backup_process_bar.set(1.)
        self.start = None
        wh.show_info('Restore successful', f'Database \'{self.server["destination"]["db"]}\' cloned successfully.')
