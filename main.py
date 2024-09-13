import customtkinter as ctk
from customtkinter import filedialog as fd

from ui.honor_page import HonorPage
from ui.start_page import StartPage


class MemberAdminApp(ctk.CTk):
    filename = ""

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    def __init__(self, f):
        self.filename = filename
        ctk.CTk.__init__(self)

        # Adjust general settings for the CTk
        self.geometry("800x800")
        self.title("Mitglieder Management Portal")

        # General Page overview including title
        title = ctk.CTkLabel(self, text="Mitglieder Management Portal")
        title.pack(pady=20)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = ctk.CTkFrame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)



        # Frame Switcher
        self.frames = {}
        for F in (StartPage, HonorPage):
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
