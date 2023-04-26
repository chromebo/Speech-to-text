import time
import pyaudio
import multiprocessing as mp
import tkinter as tk
import wave
import speech_recognition as sr


def rec(sample_format, rate, chunk, frames, q):
    print("enable_rec")
    p = pyaudio.PyAudio()
    stream = p.open(format=sample_format, channels=1, rate=rate, frames_per_buffer=chunk,
                    input_device_index=1,
                    input=True)

    while True:
        for i in range(0, int(rate / chunk * 10)):
            data = stream.read(chunk)
            frames.append(data)
        q.put(frames)
        frames = []


def recognition(filename, rate,  q, text):
    with open("text.txt", "w") as source:
        source.write("")
    while True:
        time.sleep(10)
        print("enable_recog")
        frames = q.get()
        q.empty()

        wf = wave.open(filename, "wb")
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        frames = []

        rec = sr.Recognizer()
        sample = sr.WavFile(filename)

        with sample as source:
            rec.adjust_for_ambient_noise(source)
            data = rec.record(source)
            try:
                text = rec.recognize_google(data, language='ru')
            except sr.UnknownValueError:
                recognition(filename, rate,  q, text)
            except sr.RequestError:
                print("Отсутствует подключение к интернету")
                recognition(filename, rate,  q, text)
        print(text)
        with open("text.txt", "a") as source:
            source.write(f"{text}.")


if __name__ == '__main__':
    sample_format = pyaudio.paInt16  # 16 бит на выборку
    filename = "output_sound.wav"
    chunk = 1024  # Запись кусками по 1024 сэмпла
    rate = 44100
    changer = True
    frames = []
    text = None
    q = mp.Queue()

    proc_rec = mp.Process(target=rec, args=(sample_format, rate, chunk, frames, q), daemon=True)
    proc_recog = mp.Process(target=recognition, args=(filename, rate,  q, text), daemon=True)

    def update():
        with open("text.txt", "r") as source:
            res = source.read()
        with open("text.txt", "w") as source:
            source.write("")
        large_text.insert(tk.END, res)

    def save():
        result = large_text.get(1.0, 'end')
        with open("result.txt", "a") as source:
            source.write(f"{result}")

    window = tk.Tk()

    frame_text = tk.Frame(master=window)
    large_text = tk.Text(master=frame_text)

    frame_buttons = tk.Frame(master=window)
    button_update = tk.Button(master=frame_buttons, command=update, text="Update")
    button_save = tk.Button(master=frame_buttons, command=save, text="Save")

    frame_buttons.grid()
    button_save.grid(column=0, row=0)
    button_update.grid(column=1, row=0)

    frame_text.grid()
    large_text.grid()

    proc_rec.start()
    proc_recog.start()

    window.mainloop()