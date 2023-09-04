from dotenv import load_dotenv
from chromadb.config import Settings
import os
import chromadb
from chromadb.utils import embedding_functions
from chromadb.api.models.Collection import Collection
import openai
import uuid
from collections.abc import Sequence
import json
from functools import partial
import threading
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfile

from utils import synopsis_explanation
from listener import listen
from narratives.models import get_narrative_from_json, NarrativeEncoder

load_dotenv()  # take environment variables from .env.

# Code of your application, which uses environment variables (e.g. from `os.environ` or
# `os.getenv`) as if they came from the actual environment.

openai_api_key = os.getenv("OPENAI_API_KEY")


openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=openai_api_key,
    model_name="text-embedding-ada-002"
)
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="data"
))


def insert_data(story_name: str):
    # Visit stories directory and insert all json files inside of directory titled story_name
    # into the database
    # TODO: Implement
    for file in os.listdir(f"stories/{story_name}"):
        if file.endswith(".json"):
            with open(f"stories/{story_name}/{file}", "r") as f:
                client.insert(f.read())  # TODO: Fix this


def get_story_settings(story_name: str) -> dict:
    story_settings = {}
    for file in os.listdir(f"stories/{story_name}"):
        if file.endswith(".json"):
            with open(f"stories/{story_name}/{file}", "r") as f:
                data = json.load(f)
                story_settings = data
    return story_settings


def prompt_for_story_outline(story_name: str):
    # Prompt openai for story outline using embeddings
    # TODO: Implement
    return ""


def get_embedding(text, model="text-embedding-ada-002") -> list:
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=[text], model=model)['data'][0]['embedding']


def create_new_story():
    user_input = input("Enter a new story name: ")
    if user_input:
        # Set new story name to user input with no spaces and all lowercase and underscores instead of spaces
        original_story_name = user_input
        new_story_name = user_input.replace(" ", "_").lower()
        new_collection = client.create_collection(
            name=new_story_name, embedding_function=openai_ef)
        print(f"Story {original_story_name} created")

        # Get openai embeddings for story title
        # story_title_embeddings = get_embedding(original_story_name)
        # print(story_title_embeddings)
        new_collection.add(
            ids=[str(uuid.uuid4())],
            documents=[original_story_name],
            metadatas=[{"story_title": original_story_name}]
        )


def delete_story():
    user_input = input("Enter a story name to delete: ")
    if user_input:
        new_story_name = user_input.replace(" ", "_").lower()
        try:
            client.delete_collection(name=new_story_name)
            print(f"Story {new_story_name} deleted")
        except IndexError:
            print("Story does not exist")
        except ValueError:
            print("Story does not exist")


root = Tk()
root.title("Story Traveler")
root.resizable(True, True)
root.geometry("800x600")

frm = ttk.Frame(root, padding=10)
frm.grid()

current_narrative = None


def save_story() -> None:
    global current_narrative
    if current_narrative is not None:
        with open(f"stories/{current_narrative.id}/settings.json", "w") as f:
            json.dump(current_narrative, f, cls=NarrativeEncoder, indent=2)
            f.write('\n')


def save_synopsis() -> None:
    global current_narrative
    if current_narrative is not None:
        current_narrative.synopsis = chtext.get("1.0", END)


def save_action() -> None:
    save_synopsis()
    save_story()


def load_synopsis() -> None:
    global current_narrative
    if current_narrative is not None:
        chtext.insert(END, current_narrative.synopsis)


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
        global current_narrative
        content = file.read()
        current_narrative = get_narrative_from_json(content)
        story_title_label.configure(text=current_narrative.title)


def main():
    menu_bar = Menu(root)
    file_menu = Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Open", command=partial(open_file))
    file_menu.add_command(label="Quit", command=root.destroy)

    menu_bar.add_cascade(label="File", menu=file_menu)
    root.config(menu=menu_bar)

    story_title_label = ttk.Label(frm, text="Story title")
    story_title_label.grid(column=0, row=0)
    synopsis_button = ttk.Button(frm, text="Synopsis", command=partial(
        load_synopsis))
    synopsis_button.grid(column=0, row=1)

    # Save the current text in the text box to the database and settings file
    # if necessary
    save_button = ttk.Button(frm, text="Save", command=partial(save_action))
    save_button.grid(column=2, row=0)

    ttk.Label(frm, text="Talk about a character").grid(column=3, row=0)
    speak_button = ttk.Button(frm, text="Speak", command=partial(
        get_audio))
    speak_button.grid(column=4, row=0)

    # Text box for the user to enter text and load text from the database
    # and settings file
    chtext = Text(frm, width=40, height=10)
    chtext.grid(column=2, row=2, columnspan=2)

    root.mainloop()


if __name__ == "__main__":
    main()
