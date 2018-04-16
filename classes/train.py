import os
import time
import wave
from Tkinter import *

import matplotlib
import pyaudio
from pydub import AudioSegment
from scipy.io import wavfile

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

import math

path = "test_data/recording/"
recording = path + "recording.wav"

wave_sums = []
durations = []

class Train:

    # sound is a pydub.AudioSegment
    # silence_threshold in dB
    # chunk_size in ms

    # iterate over chunks until you find the first one with sound
    def detect_leading_silence(self, sound, silence_threshold=-28.0, chunk_size=10):
        trim_ms = 0  # ms
        assert chunk_size > 0  # to avoid infinite loop
        while sound[trim_ms:trim_ms + chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
            trim_ms += chunk_size
        return trim_ms

    def record_audio(self):
        chunk = 1024
        format = pyaudio.paInt16
        channels = 2
        rate = 44100
        record_seconds = 1
        output_dir = "test_data/" + self.txt_dropdown.get() + "/"
        file_number = len(os.listdir(output_dir))

        p = pyaudio.PyAudio()

        stream = p.open(format=format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)

        print("* recording " + str(file_number))

        frames = []
        for i in range(0, int(rate / chunk * record_seconds)):
            data = stream.read(chunk)
            frames.append(data)

        print("* done recording")

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(recording, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        self.train(output_dir)
        os.remove(recording)

    def train(self, save_path):
        tempfilename = recording
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
        global durations, wave_sums
        data_directory = ["test_data/Kick", "test_data/HiHat", "test_data/Snare"]
        kick_wavelengths = []
        snare_wavelengths = []
        hihat_wavelengths = []
        kick_duration = []
        snare_duration = []
        hihat_duration = []
        for dir in data_directory:
            for file in os.listdir(dir):
                filepath = dir + '/' + file
                if filepath.find(".wav") and file[0] != ".":
                    rate, data = wavfile.read(filepath)
                    mono = []
                    for sample in data:
                        avg = sample[0] + sample[1]
                        avg = avg / 2

                        mono.append(avg)

                    if len(mono) < 10000 and len(mono) > 0:
                        if dir == "test_data/Kick":
                            kick_duration.append(len(mono))
                        elif dir == "test_data/HiHat":
                            hihat_duration.append(len(mono))
                        elif dir == "test_data/Snare":
                            snare_duration.append(len(mono))
                    else:
                        os.remove(filepath)

                    index = 0
                    wavelength_transitions = []
                    for value in mono:
                        if index + 1 < len(mono) and mono[index] < 0 and mono[index + 1] > 0:
                            wavelength_transitions.append(index)
                        index += 1

                    wave_index = 0
                    wavelengths = []
                    for value in wavelength_transitions:
                        if wave_index + 2 < len(wavelength_transitions):
                            wavelengths.append(wavelength_transitions[wave_index + 2] - wavelength_transitions[wave_index])
                        wave_index += 2

                    if dir == "test_data/Kick":
                        kick_wavelengths.append(wavelengths)
                    elif dir == "test_data/HiHat":
                        hihat_wavelengths.append(wavelengths)
                    elif dir == "test_data/Snare":
                        snare_wavelengths.append(wavelengths)

        avg_kick_wave = []

        for wav in kick_wavelengths:
            wave_sum = 0
            for wavelength in wav:
                wave_sum += wavelength
            if len(wav) == 0:
                avg_kick_wave.append(wave_sum)
            else:
                avg_kick_wave.append(wave_sum / len(wav))

        avg_hihat_wave = []

        for wav in hihat_wavelengths:
            wave_sum = 0
            for wavelength in wav:
                wave_sum += wavelength
            if len(wav) == 0:
                avg_hihat_wave.append(wave_sum)
            else:
                avg_hihat_wave.append(wave_sum / len(wav))

        avg_snare_wave = []

        for wav in snare_wavelengths:
            wave_sum = 0
            for wavelength in wav:
                wave_sum += wavelength
            if len(wav) == 0:
                avg_snare_wave.append(wave_sum)
            else:
                avg_snare_wave.append(wave_sum / len(wav))

        kick_sum = sum(avg_kick_wave) / float(len(avg_kick_wave))
        hihat_sum = sum(avg_hihat_wave) / float(len(avg_hihat_wave))
        snare_sum = sum(avg_snare_wave) / float(len(avg_snare_wave))

        avg_kick_duration = sum(kick_duration) / float(len(kick_duration))
        avg_hihat_duration = sum(hihat_duration) / float(len(hihat_duration))
        avg_snare_duration = sum(snare_duration) / float(len(snare_duration))

        plt.scatter(kick_duration, avg_kick_wave, s=None, c="red")
        plt.scatter(snare_duration, avg_snare_wave, s=None, c="green")
        plt.scatter(hihat_duration, avg_hihat_wave, s=None, c="royalblue")

        durations.append(avg_kick_duration)
        durations.append(avg_hihat_duration)
        durations.append(avg_snare_duration)

        wave_sums.append(kick_sum)
        wave_sums.append(hihat_sum)
        wave_sums.append(snare_sum)

        plt.scatter([avg_kick_duration, avg_hihat_duration, avg_snare_duration], [kick_sum, hihat_sum, snare_sum], s=None,
                    c="orange")
        plt.title("Sound Classifier")
        plt.xlabel("Duration")
        plt.ylabel("Num of Waves")
        plt.show()

    def test_data(self):
        global durations, wave_sums
        kick_wavelengths = []
        snare_wavelengths = []
        hihat_wavelengths = []
        kick_duration = []
        snare_duration = []
        hihat_duration = []
        data_directory = ["test_data/testing/Kick", "test_data/testing/HiHat", "test_data/testing/Snare"]

        for dir in data_directory:
            for file in os.listdir(dir):
                filepath = dir + '/' + file

                if filepath.find(".wav") and file[0] != ".":
                    rate, data = wavfile.read(filepath)
                    mono = []
                    for sample in data:
                        avg = sample[0] + sample[1]
                        avg = avg / 2

                        mono.append(avg)

                    if len(mono) < 10000 and len(mono) > 0:
                        if dir == "test_data/testing/Kick":
                            kick_duration.append(len(mono))
                        elif dir == "test_data/testing/HiHat":
                            hihat_duration.append(len(mono))
                        elif dir == "test_data/testing/Snare":
                            snare_duration.append(len(mono))
                    else:
                        os.remove(filepath)

                    index = 0
                    wavelength_transitions = []
                    for value in mono:
                        if index + 1 < len(mono) and mono[index] < 0 and mono[index + 1] > 0:
                            wavelength_transitions.append(index)
                        index += 1

                    wave_index = 0
                    wavelengths = []
                    for value in wavelength_transitions:
                        if wave_index + 2 < len(wavelength_transitions):
                            wavelengths.append(
                                wavelength_transitions[wave_index + 2] - wavelength_transitions[wave_index])
                        wave_index += 2

                    if dir == "test_data/testing/Kick":
                        kick_wavelengths.append(wavelengths)
                    elif dir == "test_data/testing/HiHat":
                        hihat_wavelengths.append(wavelengths)
                    elif dir == "test_data/testing/Snare":
                        snare_wavelengths.append(wavelengths)

        avg_kick_wave = []

        for wav in kick_wavelengths:
            wave_sum = 0
            for wavelength in wav:
                wave_sum += wavelength
            if len(wav) == 0:
                avg_kick_wave.append(wave_sum)
            else:
                avg_kick_wave.append(wave_sum / len(wav))

        avg_hihat_wave = []

        for wav in hihat_wavelengths:
            wave_sum = 0
            for wavelength in wav:
                wave_sum += wavelength
            if len(wav) == 0:
                avg_hihat_wave.append(wave_sum)
            else:
                avg_hihat_wave.append(wave_sum / len(wav))

        avg_snare_wave = []

        for wav in snare_wavelengths:
            wave_sum = 0
            for wavelength in wav:
                wave_sum += wavelength
            if len(wav) == 0:
                avg_snare_wave.append(wave_sum)
            else:
                avg_snare_wave.append(wave_sum / len(wav))


        from_kick = []
        from_snare = []
        from_hihat = []
        for j in range(3):
            for i in range(10):
                from_kick.append(math.hypot(kick_duration[i] - durations[j], avg_kick_wave[i] - wave_sums[j]))
                from_hihat.append(math.hypot(hihat_duration[i] - durations[j], avg_hihat_wave[i] - wave_sums[j]))
                from_snare.append(math.hypot(snare_duration[i] - durations[j], avg_snare_wave[i] - wave_sums[j]))

        compare = []
        kick_predictor = [0, 0, 0, 0]
        hihat_predictor = [0,0,0,0]
        snare_predictor = [0,0,0,0]
        for i in range(30):
            compare = []
            compare.append(from_kick[i])
            compare.append(from_hihat[i])
            compare.append(from_snare[i])
            min_val = min(compare)

            # True positive
            if min_val in from_kick and i < 10:
                kick_predictor[0] += 1
            # False Negative
            elif not min_val in from_kick and i < 10:
                kick_predictor[1] += 1
            # False Positive
            elif min_val in from_kick and i >= 10:
                kick_predictor[2] += 1
            # De Morgan's law for proper negation
            # True negative
            elif not min_val in from_kick or not i >= 10:
                kick_predictor[3] += 1


            # True positive
            if min_val in from_hihat and i >= 10 and i < 20:
                hihat_predictor[0] += 1
            # False Negative
            elif not min_val in from_hihat and i >= 10 and i < 20:
                hihat_predictor[1] += 1
            # False Positive
            elif min_val in from_hihat and not (i >= 10 and i < 20):
                hihat_predictor[2] += 1
            # De Morgan's law for proper negation
            # True negative
            elif not min_val in from_hihat or not (i >= 10 and i < 20):
                hihat_predictor[3] += 1


            # True positive
            if min_val in from_snare and i >= 20:
                snare_predictor[0] += 1
            # False Negative
            elif not min_val in from_snare and i >= 20:
                snare_predictor[1] += 1
            # False Positive
            elif min_val in from_snare and i < 20:
                snare_predictor[2] += 1
            # De Morgan's law for proper negation
            # True negative
            elif not min_val in from_snare or not i < 20:
                snare_predictor[3] += 1

        print "kick predictor: " + str(kick_predictor)
        print "hihat predictor: " + str(hihat_predictor)
        print "snare predictor: " + str(snare_predictor)


    def __init__(self):
        self.root = Tk()
        self.root.title("Training")
        self.root.minsize(width=300, height=300)

        self.txt_dropdown = StringVar(self.root)
        self.txt_dropdown.set("None")
        self.dropdown = OptionMenu(self.root, self.txt_dropdown, "Kick", "Snare", "HiHat")

        self.btn_record = Button(self.root, text="Record", command=lambda: self.record_timer())

        self.btn_train = Button(self.root, text="Train Data", command=lambda: self.train_data())
        self.btn_test = Button(self.root, text="Test Data", command=lambda: self.test_data())

        self.lbl_rec = Label(self.root, text="")

        self.dropdown.pack()
        self.btn_record.pack()
        self.btn_train.pack()
        self.btn_test.pack()
        self.lbl_rec.pack()

        mainloop()
