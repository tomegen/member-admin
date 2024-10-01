import os
import customtkinter

if __name__ == '__main__':
    customtkinter_path = os.path.dirname(os.path.abspath(customtkinter.__file__))
    os.system("pyinstaller --onedir --windowed --icon member.ico --add-data " + customtkinter_path + ";customtkinter/ mitgliederverwaltung.py")