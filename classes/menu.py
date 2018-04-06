from tkinter import *
import tkinter.filedialog as filedialog
import pyaudio
import wave
from classes.train import Train


class Menu:
    def test(self):
        for i in range(10):
            if i % 2 == 0:
                record_audio(index=i)

    def record_audio(self, index):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        RECORD_SECONDS = 2
        WAVE_OUTPUT_FILENAME = "test_data/output" + str(index) + ".wav"

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print("* recording")

        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("* done recording")

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

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

        txt_kick = "No Kick Selected..."
        txt_snare = "No Snare Selected..."
        txt_hihat = "No HiHat Selected..."

        lbl_kick = Label(self.root, text=txt_kick)
        lbl_snare = Label(self.root, text=txt_snare)
        lbl_hihat = Label(self.root, text=txt_hihat)

        btn_kick = Button(self.root, text="Add Kick", command=lambda: self.open_folder(lbl_kick))
        btn_snare = Button(self.root, text="Add Snare", command=lambda: self.open_folder(lbl_snare))
        btn_hihat = Button(self.root, text="Add HiHat", command=lambda: self.open_folder(lbl_hihat))
        btn_tryout = Button(self.root, text="Try out the Instruments", command=lambda: try_instruments(lbl_kick["text"], lbl_snare["text"], lbl_hihat["text"]))
        btn_train = Button(self.root, text="Train Audio", command=lambda: Train())

        btn_kick.grid(row=0, column=0, padx=10, pady=10)
        btn_snare.grid(row=1, column=0, padx=10, pady=10)
        btn_hihat.grid(row=2, column=0, padx=10, pady=10)
        btn_tryout.grid(row=4, column=0, padx=20, pady=20)
        btn_train.grid(row=5, column=0, padx=20, pady=20)

        lbl_kick.grid(row=0, column=1, padx=10, pady=10)
        lbl_snare.grid(row=1, column=1, padx=10, pady=10)
        lbl_hihat.grid(row=2, column=1, padx=10, pady=10)

        mainloop()

