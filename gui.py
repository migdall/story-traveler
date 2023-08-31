from functools import partial
import threading
from tkinter import *
from tkinter import ttk

from listener import listen


root = Tk()
root.title("Story Traveler")
root.resizable(True, True)
root.geometry("500x500")

frm = ttk.Frame(root, padding=10)
frm.grid()


def get_audio() -> None:
    def callback():
        speak_button.configure(state="disabled")
        audio_gathered, audio_text = listen()
        print(audio_gathered)
        if audio_gathered:
            chtext.insert(END, audio_text)
        speak_button.configure(state="enabled")
    a_thread = threading.Thread(target=callback)
    a_thread.start()


ttk.Label(frm, text="Talk about a character").grid(column=0, row=0)
speak_button = ttk.Button(frm, text="Speak", command=partial(
    get_audio))
speak_button.grid(column=1, row=0)
ttk.Button(frm, text="Quit", command=root.destroy).grid(column=0, row=1)
chtext = Text(frm, width=40, height=10)
chtext.grid(column=0, row=2, columnspan=2)

root.mainloop()
