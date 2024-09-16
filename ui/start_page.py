import customtkinter as ctk

class StartPage(ctk.CTkFrame):

    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.controller = controller

        # Current members
        member_count = "Aktuelle Mitglieder: " + str(controller.members.calculate_members())
        label = ctk.CTkLabel(self, text=member_count, font=("Arial", 25, "bold"), text_color="#ffffff")
        label.pack(side="top", fill="x", pady=40)

        # New members
        new_member_count = "Neue Mitglieder in diesem Kalenderjahr: " + str(controller.members.calculate_new_members())
        label = ctk.CTkLabel(self, text=new_member_count, font=("Arial", 20, "bold"), text_color="#ffffff")
        label.pack(side="top", fill="x", pady=30)



        birthday_button = ctk.CTkButton(self, text="Geburtstage", font=("Arial", 20, "bold"), border_spacing=20, width=400,
                                        text_color="#ffffff", command=lambda: controller.show_frame("BirthdayPage"))
        birthday_button.pack(pady=20)

        honor_button = ctk.CTkButton(self, text="Ehrungen", font=("Arial", 20, "bold"), border_spacing=20,width=400,
                                     text_color="#ffffff", command=lambda: controller.show_frame("HonorPage"))
        honor_button.pack(pady=20)

