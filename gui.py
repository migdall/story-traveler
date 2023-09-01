from functools import partial
import threading
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfile

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


def open_file() -> None:
    file = askopenfile(mode="r", filetypes=[("JSON Files", "*.json")])
    if file is not None:
        content = file.read()
        print(content)


menu_bar = Menu(root)
file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open", command=partial(open_file))
file_menu.add_command(label="Quit", command=root.destroy)

menu_bar.add_cascade(label="File", menu=file_menu)
root.config(menu=menu_bar)

ttk.Label(frm, text="Talk about a character").grid(column=0, row=0)
speak_button = ttk.Button(frm, text="Speak", command=partial(
    get_audio))
speak_button.grid(column=1, row=0)
chtext = Text(frm, width=40, height=10)
chtext.grid(column=0, row=2, columnspan=2)

root.mainloop()
