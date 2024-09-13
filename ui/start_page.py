import customtkinter as ctk
from logic.members import Members


class StartPage(ctk.CTkFrame):

    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.controller = controller

        members = Members(controller.filename)

        # Current members
        member_count = "Aktuelle Mitglieder: " + str(members.calculate_members())
        label = ctk.CTkLabel(self, text=member_count)
        label.pack(side="top", fill="x", pady=10)

        # New members
        new_member_count = "Neue Mitglieder in diesem Kalenderjahr: " + str(members.calculate_new_members())
        label = ctk.CTkLabel(self, text=new_member_count)
        label.pack(side="top", fill="x", pady=10)



        button = ctk.CTkButton(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()

