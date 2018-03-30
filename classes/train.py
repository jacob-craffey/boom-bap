from tkinter import *
import wave
import pyaudio


class Train:
    def record_audio(self, index):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        RECORD_SECONDS = 2
        WAVE_OUTPUT_FILENAME = "test_data/" + self.txt_dropdown.get() + "/" + str(index/2) + ".wav"

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        self.lbl_rec["text"] = "RECORDING"
        print("* recording " + str(index/2))


        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("* done recording")
        self.lbl_rec["text"] = "PAUSE"

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

    def test(self):
        for i in range(10):
            if i % 2 == 0:
                self.record_audio(index=i)

    def __init__(self):
        self.root = Tk()
        self.root.title("Training")
        self.root.minsize(width=300, height=300)

        self.txt_dropdown = StringVar(self.root)
        self.txt_dropdown.set("None")
        self.dropdown = OptionMenu(self.root, self.txt_dropdown, "Kick", "Snare", "HiHat")

        self.btn_record = Button(self.root, text="Record", command=lambda: self.test())

        self.lbl_rec = Label(self.root, text="")

        self.dropdown.pack()
        self.btn_record.pack()
        self.lbl_rec.pack()

        mainloop()
