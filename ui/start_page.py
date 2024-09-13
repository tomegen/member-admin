import customtkinter as ctk


class StartPage(ctk.CTkFrame):

    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.controller = controller

        # Current members
        member_count = "Aktuelle Mitglieder: " + str(controller.members.calculate_members())
        label = ctk.CTkLabel(self, text=member_count)
        label.pack(side="top", fill="x", pady=10)

        # New members
        new_member_count = "Neue Mitglieder in diesem Kalenderjahr: " + str(controller.members.calculate_new_members())
        label = ctk.CTkLabel(self, text=new_member_count)
        label.pack(side="top", fill="x", pady=10)



        button = ctk.CTkButton(self, text="Geburtstage",
                           command=lambda: controller.show_frame("BirthdayPage"))
        button.pack()

