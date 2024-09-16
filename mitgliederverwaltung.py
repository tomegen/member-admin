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
        self.geometry("700x700")
        self.title("Mitglieder Management Portal")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = ctk.CTkFrame(self, width=700, height=700, corner_radius=10,bg_color="#1a1a1a",
                                 fg_color="#2a2a2a", border_color="#4a4a4a", border_width=2)


        container.place_configure(
            x=0,
            y=0,
            relwidth=1,
            relheight=1
        )

        container.pack(expand=True)

        # Frame Switcher
        self.frames = {}
        for F in (StartPage, BirthdayPage, HonorPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

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
