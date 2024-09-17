import customtkinter as ctk
import pandas as pd
from tkcalendar import DateEntry
from customtkinter import filedialog as fd
from tkinter import messagebox as mb
from logic.birthday_calculation import write_birthdays_into_txt, write_birthdays_into_ics


class BirthdayPage(ctk.CTkFrame):

    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.controller = controller

        # create overall frame for the date time picker
        self.date_range_frame = ctk.CTkFrame(self,
                                             fg_color="#2a2d2e")
        self.date_range_frame.pack(side="top", padx=20, pady=20)

        # Create the start date widget
        self.start_date_label = ctk.CTkLabel(self.date_range_frame,
                                             text="Start Date:",
                                             font=("Arial", 20, "bold"),
                                             text_color="#ffffff")
        self.start_date_label.pack(side="left", padx=10, pady=10)

        # Create the start_date date entry
        self.start_date = DateEntry(self.date_range_frame,
                                    width=12,
                                    background='darkblue',
                                    font=("Arial", 20, "bold"),
                                    text_color="#ffffff",
                                    foreground='white',
                                    borderwidth=2,
                                    date_pattern='yyyy-mm-dd')
        self.start_date.pack(side="left", padx=10, pady=10)

        # Create the end date widget
        self.end_date_label = ctk.CTkLabel(self.date_range_frame,
                                           text="End Date:",
                                           font=("Arial", 20, "bold"),
                                           text_color="#ffffff")
        self.end_date_label.pack(side="left", padx=10, pady=10)

        # Create the end_date date entry
        self.end_date = DateEntry(self.date_range_frame,
                                  width=12,
                                  background='darkblue',
                                  font=("Arial", 20, "bold"),
                                  text_color="#ffffff",
                                  foreground='white',
                                  borderwidth=2,
                                  date_pattern='yyyy-mm-dd')
        self.end_date.pack(side="left", padx=10, pady=10)


        # DateRange
        label = ctk.CTkLabel(self,
                             text="Wähle alle Geburtstage, die kalkuliert werden sollen",
                             font=("Arial", 20, "bold"),
                             text_color="#ffffff")
        label.pack(side="top", fill="x", pady=10)

        # Create a scrollable frame with all the birthday possibilities inside
        scrollable_frame = ctk.CTkScrollableFrame(self,
                                                  fg_color="#2a2d2e")
        scrollable_frame.pack(pady=20)

        # create all the checkboxes for all the birthdays that are possible
        self.birthday_buttons = []
        for birthday_config in controller.config.birthday_config:
            checkbox_value = ctk.BooleanVar()
            checkbox_value.set(True)
            check_box = ctk.CTkCheckBox(scrollable_frame,
                                        text=str(birthday_config) + ". Geburtstag",
                                        onvalue=True,
                                        offvalue=False,
                                        variable=checkbox_value,
                                        font=("Arial", 15, "bold"),
                                        text_color="#ffffff")
            check_box.pack(pady=5)
            self.birthday_buttons.append(checkbox_value)


        # button to generate a txt file
        generate_txt_file_button = ctk.CTkButton(self,
                                                 text="Erstelle text-Datei",
                                                 font=("Arial", 20, "bold"),
                                                 text_color="#ffffff",
                                                 border_spacing=10,
                                                 width=400,
                                                 command=lambda: self.create_txt_birthday_file(
                                                     from_date=pd.to_datetime(str(self.start_date.get_date())),
                                                     to_date=pd.to_datetime(str(self.end_date.get_date()))))
        generate_txt_file_button.pack(pady=10)

        # button to generate an ics file
        generate_ics_file_button = ctk.CTkButton(self,
                                                 text="Erstelle Kalender (ics) Datei",
                                                 font=("Arial", 20, "bold"),
                                                 text_color="#ffffff",
                                                 border_spacing=10,
                                                 width=400,
                                                 command=lambda: self.create_ics_birthday_file(
                                                     from_date=pd.to_datetime(str(self.start_date.get_date())),
                                                     to_date=pd.to_datetime(str(self.end_date.get_date()))))
        generate_ics_file_button.pack(pady=10)

        # show start button
        start_button = ctk.CTkButton(self,
                                     text="Startseite",
                                     font=("Arial", 20, "bold"),
                                     text_color="#ffffff",
                                     border_spacing=10,
                                     width=400,
                                     command=lambda: controller.show_frame("StartPage"))
        start_button.pack(pady=25)


    # create the txt birthday file
    def create_txt_birthday_file(self, from_date, to_date):
        txt_filename = fd.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])

        # calculate all the checked birthdays
        checked_birthdays = []
        if txt_filename:
            for i, button in enumerate(self.birthday_buttons):
                if button.get():
                    checked_birthdays.append(self.controller.config.birthday_config[i])

            if write_birthdays_into_txt(members=self.controller.members.members,
                                        birthdays=checked_birthdays,
                                        from_date=from_date,
                                        to_date=to_date,
                                        txt_filename=txt_filename):
                # Show that creation was successful
                mb.showinfo("Datei erfolgreich erstellt", "Die Datei " + txt_filename + " wurde erfolgreich erstellt.")
                print("Birthday txt file was successfully created.")

        else:
            print("Filename was not chosen: " + txt_filename)


    # function to create an ics file out of the input
    def create_ics_birthday_file(self, from_date, to_date):
        ics_filename = fd.asksaveasfilename(defaultextension=".ics",
                                            filetypes=[("Calendar Files", "*.ics"), ("All Files", "*.*")])

        # logic to calculate all the checked birthdays
        checked_birthdays = []
        if ics_filename:
            for i, button in enumerate(self.birthday_buttons):
                if button.get():
                    checked_birthdays.append(self.controller.config.birthday_config[i])

            if write_birthdays_into_ics(members=self.controller.members.members,
                                        birthdays=checked_birthdays,
                                        from_date=from_date,
                                        to_date=to_date,
                                        ics_filename=ics_filename):
                # Show that creation was successful
                mb.showinfo("Datei erfolgreich erstellt", "Die Datei " + ics_filename + " wurde erfolgreich erstellt.")
                print("Birthday ics file was successfully created.")
        else:
            print("Filename was not chosen: " + ics_filename)
