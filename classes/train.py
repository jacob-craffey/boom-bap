from tkinter import *
import wave
import pyaudio
import time
from pydub import AudioSegment
import os


class Train:
    def detect_leading_silence(self, sound, silence_threshold=-28.0, chunk_size=10):
        '''
        sound is a pydub.AudioSegment
        silence_threshold in dB
        chunk_size in ms

        iterate over chunks until you find the first one with sound
        '''
        trim_ms = 0  # ms

        assert chunk_size > 0  # to avoid infinite loop
        while sound[trim_ms:trim_ms + chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
            trim_ms += chunk_size

        return trim_ms

    def record_audio(self, index):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        RECORD_SECONDS = 2
        WAVE_OUTPUT_FILENAME = "test_data/" + self.txt_dropdown.get() + "/recording/" + str(index/2) + ".wav"

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

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

    def train(self, instrument):
        filepath = "test_data/" + instrument + "/recording/"
        directory = os.fsencode(filepath)
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith(".wav"):
                tempfilename = filepath + filename
                sound = AudioSegment.from_file(tempfilename, format="wav")
                start_trim = self.detect_leading_silence(sound)
                end_trim = self.detect_leading_silence(sound.reverse())
                duration = len(sound)
                trimmed_sound = sound[start_trim:duration - end_trim]
                trimmed_sound.export("test_data/" + instrument + "/trimmed/" + filename, format="wav")

            else:
                continue

    def record_timer(self, instrument):
        for i in range(10):
            if i % 2 == 0:
                self.record_audio(index=i)
            else:
                time.sleep(2)
        self.train(instrument)

    def __init__(self):
        self.root = Tk()
        self.root.title("Training")
        self.root.minsize(width=300, height=300)

        self.txt_dropdown = StringVar(self.root)
        self.txt_dropdown.set("None")
        self.dropdown = OptionMenu(self.root, self.txt_dropdown, "Kick", "Snare", "HiHat")

        self.btn_record = Button(self.root, text="Record", command=lambda: self.record_timer(self.txt_dropdown.get()))

        self.lbl_rec = Label(self.root, text="")

        self.dropdown.pack()
        self.btn_record.pack()
        self.lbl_rec.pack()

        mainloop()
