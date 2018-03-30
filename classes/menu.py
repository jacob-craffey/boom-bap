from tkinter import *
import tkinter.filedialog as filedialog
from classes.train import Train


class Menu:
    def open_folder(self, label):
        try:
            f = filedialog.askopenfilename(filetypes=(("WAV files", "*.wav"), ("All files", "*.*")))
            f = f.split("boom-bap", 1)[1]
            label["text"] = f
        except IndexError:
            pass

    def __init__(self):
        self.root = Tk()

        self.root.title("BoomBap")
        self.root.minsize(width=400, height=400)

        lbl_kick = Label(self.root, text="No Kick Selected..")
        lbl_snare = Label(self.root, text="No Snare Selected...")
        lbl_hihat = Label(self.root, text="No HiHat Selected...")

        btn_kick = Button(self.root, text="Add Kick", command=lambda: self.open_folder(lbl_kick))
        btn_snare = Button(self.root, text="Add Snare", command=lambda: self.open_folder(lbl_snare))
        btn_hihat = Button(self.root, text="Add HiHat", command=lambda: self.open_folder(lbl_hihat))
        btn_train = Button(self.root, text="Train Audio", command=lambda: Train())

        btn_kick.grid(row=0, column=0, padx=10, pady=10)
        btn_snare.grid(row=1, column=0, padx=10, pady=10)
        btn_hihat.grid(row=2, column=0, padx=10, pady=10)
        btn_train.grid(row=5, column=0, padx=20, pady=20)

        lbl_kick.grid(row=0, column=1, padx=10, pady=10)
        lbl_snare.grid(row=1, column=1, padx=10, pady=10)
        lbl_hihat.grid(row=2, column=1, padx=10, pady=10)

        mainloop()
