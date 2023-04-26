import keyboard
import speech_recognition as sr
import pyaudio
import wave
import clipboard
from deep_translator import GoogleTranslator


class Main:
    def __init__(self):
        self.chunk = 1024  # Запись кусками по 1024 сэмпла
        self.sample_format = pyaudio.paInt16  # 16 бит на выборку
        self.rate = 44100
        self.frames = []
        self.changer = False
        self.filename = "output_sound.wav"
        self.text = None
        keyboard.add_hotkey("alt+o", self.check_changer)
        self.p = pyaudio.PyAudio()

    def record_dec(self, func):
        def wrapper():
            self.stream = self.p.open(format=self.sample_format, channels=1, rate=self.rate, frames_per_buffer=self.chunk,
                                 input_device_index=1,
                                 input=True)

            func()

            self.stream.stop_stream()
            self.stream.close()
            self.samp_form_for_wf = self.p.get_sample_size(self.sample_format)

        return wrapper

    def record(self):
        print("Recording")
        while keyboard.is_pressed('alt+p'):
            data = self.stream.read(self.chunk)
            self.frames.append(data)

    def recognition(self):
        wf = wave.open(self.filename, "wb")
        wf.setnchannels(1)
        wf.setsampwidth(self.samp_form_for_wf)
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        rec = sr.Recognizer()

        sample = sr.WavFile(self.filename)

        self.frames = []

        with sample as source:
            rec.adjust_for_ambient_noise(source)
            data = rec.record(source)
            try:
                self.text = rec.recognize_google(data, language='ru')
            except sr.UnknownValueError:
                self.main()
            except sr.RequestError:
                print("Отсутствует подключение к интернету")
                self.main()

    def check_changer(self):
        print("Смена языка")
        self.changer = not self.changer

    def translate(self):
        self.text = GoogleTranslator(source='ru', target='en').translate(self.text)

    def insert_transcrib(self):
        clipboard.copy(self.text + ". ")
        keyboard.press("ctrl+v")
        keyboard.release('ctrl')
        keyboard.release('v')

    def main(self):
        while True:
            keyboard.wait('alt+p')
            self.record_dec(self.record)()
            self.recognition()
            if self.changer:
                self.translate()
            self.insert_transcrib()


if __name__ == "__main__":
    program = Main()
    program.main()
