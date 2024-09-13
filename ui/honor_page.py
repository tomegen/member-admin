import customtkinter as ctk


class HonorPage(ctk.CTkFrame):

    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.controller = controller
        label = ctk.CTkLabel(self, text="Wähle die richtige Mitgliedsliste")
        label.pack(side="top", fill="x", pady=10)



        button1 = ctk.CTkButton(self, text="Go to Page One",
                                command=lambda: controller.show_frame("PageOne"))
        button2 = ctk.CTkButton(self, text="Go to Page Two",
                                command=lambda: controller.show_frame("PageTwo"))
        button1.pack()
        button2.pack()
