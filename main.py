from Tkinter import *
import subprocess
import sys

def open_folder():
    subprocess.call(['xdg-open', '.'])

def initialize_menu():
    root = Tk()
    root.title("BoomBap")
    root.minsize(width=400, height=400)

    btn_kick = Button(root, text="Add Kick")
    btn_snare = Button(root, text="Add Snare")
    btn_hihat = Button(root, text="Add HiHat")

    btn_kick.pack()
    btn_snare.pack()
    btn_hihat.pack()

    mainloop()

def main():
    initialize_menu()

if __name__ == "__main__":
    main()