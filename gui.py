from functools import partial
import json
import threading
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfile

from listener import listen


root = Tk()
root.title("Story Traveler")
root.resizable(True, True)
root.geometry("800x600")

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
        print(type(content))
        content_dict = json.loads(content)
        story_title_label.configure(text=content_dict["storyTitle"])


menu_bar = Menu(root)
file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open", command=partial(open_file))
file_menu.add_command(label="Quit", command=root.destroy)

menu_bar.add_cascade(label="File", menu=file_menu)
root.config(menu=menu_bar)

story_title_label = ttk.Label(frm, text="Story title")
story_title_label.grid(column=0, row=0)
synopsis_button = ttk.Button(frm, text="Synopsis")
synopsis_button.grid(column=0, row=1)
ttk.Label(frm, text="Talk about a character").grid(column=2, row=0)
speak_button = ttk.Button(frm, text="Speak", command=partial(
    get_audio))
speak_button.grid(column=3, row=0)
chtext = Text(frm, width=40, height=10)
chtext.grid(column=2, row=2, columnspan=2)

root.mainloop()
