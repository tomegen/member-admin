import customtkinter as ctk
from customtkinter import filedialog as fd
from logic.config import Config
from logic.members import Members
from ui.birthday_page import BirthdayPage
from ui.honor_page import HonorPage
from ui.start_page import StartPage

class MemberAdminApp(ctk.CTk):

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    def __init__(self, f):
        self.filename = filename
        self.config = Config()
        self.members = Members(self.filename, self.config)

        ctk.CTk.__init__(self)

        # Adjust general settings for the CTk
        self.geometry("800x700")
        self.title("Mitglieder Management Portal")

        # Frame Switcher
        self.frames = {}
        for F in (StartPage, BirthdayPage, HonorPage):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()


if __name__ == "__main__":

    filetypes = (
        ('xlsx files', '*.xlsx'),
        ('xls files', '*.xls')
    )

    filename = fd.askopenfilename(
        title='Wähle deine Mitgliederliste aus',
        initialdir='/',
        filetypes=filetypes)

    if filename:
        app = MemberAdminApp(f=filename)
        app.mainloop()
