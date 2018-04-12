import os
import time
import wave
from Tkinter import *

import pyaudio
from pydub import AudioSegment
from scipy.io import wavfile

path = "test_data/recording/"
recording = path + "recording.wav"

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

    def record_audio(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        RECORD_SECONDS = 2
        OUTPUT_DIR = "test_data/" + self.txt_dropdown.get() + "/"
        file_number = len(os.listdir(OUTPUT_DIR))

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print("* recording " + str(file_number))

        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("* done recording")

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(recording, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        self.train(OUTPUT_DIR)
        os.remove(recording)

    def train(self, save_path):
        tempfilename = recording
        print(tempfilename)
        sound = AudioSegment.from_file(tempfilename, format="wav")
        start_trim = self.detect_leading_silence(sound)
        end_trim = self.detect_leading_silence(sound.reverse())
        duration = len(sound)
        trimmed_sound = sound[start_trim:duration - end_trim]
        trimmed_sound.export(save_path + str(len(os.listdir(save_path))) + ".wav", format="wav")

    def record_timer(self):
        for i in range(10):
            if i % 2 == 0:
                self.record_audio()
            else:
                time.sleep(2)

    def train_data(self):
        import os
        data_directory = ["test_data/Kick", "test_data/HiHat", "test_data/Snare"]
        for dir in data_directory:
            for file in os.listdir(dir):
                filepath = dir + '/' + file
                wf = wave.open(filepath, 'rb')
                rate, data = wavfile.read(filepath)
                print data

    def __init__(self):
        self.root = Tk()
        self.root.title("Training")
        self.root.minsize(width=300, height=300)

        self.txt_dropdown = StringVar(self.root)
        self.txt_dropdown.set("None")
        self.dropdown = OptionMenu(self.root, self.txt_dropdown, "Kick", "Snare", "HiHat")

        self.btn_record = Button(self.root, text="Record", command=lambda: self.record_timer())

        self.btn_train = Button(self.root, text="Train Data", command=lambda: self.train_data())

        self.lbl_rec = Label(self.root, text="")

        self.dropdown.pack()
        self.btn_train.pack()
        self.btn_record.pack()
        self.lbl_rec.pack()

        mainloop()
