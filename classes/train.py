import os
import time
import wave
from Tkinter import *

import pyaudio
from pydub import AudioSegment
from scipy.io import wavfile
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt


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
        RECORD_SECONDS = 1
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
        time.sleep(1)
        for i in range(220):
            if i % 2 == 0:
                self.record_audio()
            else:
                time.sleep(2)

    def train_data(self):
        import os
        data_directory = ["test_data/Kick", "test_data/HiHat", "test_data/Snare"]
        kickWavelengths = []
        snareWavelengths = []
        hiHatWavelengths = []
        kickDuration = []
        snareDuration = []
        hihatDuration = []
        for dir in data_directory:
            print dir
            for file in os.listdir(dir):
                filepath = dir + '/' + file
                if filepath.find(".wav") and file[0] != ".":
                    rate, data = wavfile.read(filepath)
                    # print data
                    mono = []
                    for sample in data:
                        avg = sample[0] + sample[1]
                        avg = avg / 2

                        mono.append(avg)

                    if len(mono) < 10000 and len(mono) > 0:
                        if dir == "test_data/Kick":
                            kickDuration.append(len(mono))
                        elif dir == "test_data/HiHat":
                            hihatDuration.append(len(mono))
                        elif dir == "test_data/Snare":
                            snareDuration.append(len(mono))
                    else:
                        os.remove(filepath)

                    index = 0
                    wavelengthTransitions = []
                    for value in mono:
                        if index+1 < len(mono) and mono[index] < 0 and mono[index+1] > 0:
                            # print "Crossed Zero at " + str(index)
                            wavelengthTransitions.append(index)
                        index += 1
                    # print wavelengthTransitions

                    waveIndex = 0
                    wavelengths = []
                    for value in wavelengthTransitions:
                        if waveIndex+2 < len(wavelengthTransitions):
                            wavelengths.append(wavelengthTransitions[waveIndex + 2] - wavelengthTransitions[waveIndex])
                        waveIndex += 2

                    if dir == "test_data/Kick":
                        kickWavelengths.append(wavelengths)
                    elif dir == "test_data/HiHat":
                        hiHatWavelengths.append(wavelengths)
                    elif dir == "test_data/Snare":
                        snareWavelengths.append(wavelengths)

        kickWaveAverage = []

        for wav in kickWavelengths:
            wavSum = 0
            for wavelength in wav:
                wavSum += wavelength
            print len(wav)
            if len(wav) == 0:
                kickWaveAverage.append(wavSum)
            else:
                kickWaveAverage.append(wavSum / len(wav))


        hihatWaveAverage = []

        for wav in hiHatWavelengths:
            wavSum = 0
            for wavelength in wav:
                wavSum += wavelength
            if len(wav) == 0:
                hihatWaveAverage.append(wavSum)
            else:
                hihatWaveAverage.append(wavSum / len(wav))

        snareWaveAverage = []

        for wav in snareWavelengths:
            wavSum = 0
            for wavelength in wav:
                wavSum += wavelength
            if len(wav) == 0:
                snareWaveAverage.append(wavSum)
            else:
                snareWaveAverage.append(wavSum / len(wav))




        kicksum = sum(kickWaveAverage) / float(len(kickWaveAverage))
        hihatsum = sum(hihatWaveAverage) / float(len(hihatWaveAverage))
        snaresum = sum(snareWaveAverage) / float(len(snareWaveAverage))


        print "kick wave average" + str(kickWaveAverage)
        print "hihat wave average" + str(hihatWaveAverage)
        print "snare wave average" + str(snareWaveAverage)





        avgkickDuration = sum(kickDuration) / float(len(kickDuration))
        avghihatDuration = sum(hihatDuration) / float(len(hihatDuration))
        avgsnareDuration = sum(snareDuration) / float(len(snareDuration))

        print "kick duration" + str(kickDuration)
        print "snare duration" + str(snareDuration)
        print "hihat duration" + str(hihatDuration)
        print "kick waves" + str(kickWavelengths)
        plt.scatter(kickDuration, kickWaveAverage, s=None, c="red")
        plt.scatter(snareDuration, snareWaveAverage, s=None, c="green")
        plt.scatter(hihatDuration, hihatWaveAverage, s=None, c="royalblue")

        plt.scatter([avgkickDuration, avghihatDuration, avgsnareDuration],[kicksum, hihatsum, snaresum], s=None, c="orange")
        plt.title("Sound Classifier (n=3)")
        plt.xlabel("Duration (1 mb / sec)  --Lowpass filter set at -28db")
        plt.ylabel("Num of Waves")
        plt.show()


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
