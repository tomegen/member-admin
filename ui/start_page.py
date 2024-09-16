import customtkinter as ctk


class StartPage(ctk.CTkFrame):

    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.controller = controller

        # Current members
        member_count = "Aktuelle Mitglieder: " + str(controller.members.calculate_members())
        label = ctk.CTkLabel(self, text=member_count, font=("Arial", 20, "bold"), text_color="#ffffff")
        label.pack(side="top", fill="x")

        # New members
        new_member_count = "Neue Mitglieder in diesem Kalenderjahr: " + str(controller.members.calculate_new_members())
        label = ctk.CTkLabel(self, text=new_member_count, font=("Arial", 20, "bold"), text_color="#ffffff")
        label.pack(side="top", fill="x")



        birthday_button = ctk.CTkButton(self, text="Geburtstage",
                           command=lambda: controller.show_frame("BirthdayPage"))
        birthday_button.pack()

        honor_button = ctk.CTkButton(self, text="Ehrungen",
                                        command=lambda: controller.show_frame("HonorPage"))
        honor_button.pack()

