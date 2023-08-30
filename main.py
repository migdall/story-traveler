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
import curses
from curses import wrapper

from utils import synopsis_explanation
from listener import listen

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


def prompt_for_story_synopsis(stdscr, collection: Collection, story_title: str) -> str:
    """ Ask for story synopsis """
    stdscr.addstr(
        f"Enter a story synopsis for {story_title}: \n {synopsis_explanation}")

    # Loop until user states they are happy with the synopsis
    stdscr.addstr("Enter a story synopsis: ")
    output = ""
    # Display the options for the user to type or speak
    stdscr.addstr("\n\nOptions:\n")
    stdscr.addstr("1. Type\n")
    stdscr.addstr("2. Speak\n")

    # Get user choice
    stdscr.addstr("Choice: ")
    choice = int(stdscr.getkey())
    stdscr.addstr(str(choice))
    stdscr.getch()

    if choice == 1:
        stdscr.addstr("\nType: ")
        while True:
            user_input = stdscr.getkey()
            stdscr.addstr(user_input)

            output += user_input

            if user_input == "\n":
                break
    elif choice == 2:
        stdscr.addstr("\nSpeak")
        user_satified = False
        while not user_satified:
            # Listen for user input
            audio_gathered, text = listen()
            if audio_gathered:
                stdscr.addstr(f"\n\nAudio gathered: {text}")
                stdscr.addstr("Are you satisfied with this audio? (y/n): ")
                user_input = stdscr.getkey()
                stdscr.addstr(user_input)
                if user_input == "n":
                    stdscr.addstr(
                        "\nDo you want to edit the text? (y/n): ")
                    user_input = stdscr.getkey()
                    stdscr.addstr(user_input)

                    if user_input == "y":
                        stdscr.addstr("\nEdit the text: ")
                        stdscr.addstr(text)
                        user_input = stdscr.getkey()
                        stdscr.addstr(user_input)
                        output += user_input
                        if user_input == "\n":
                            break
                user_satified = True
                output = text
            else:
                stdscr.addstr(f"Error: {text}")
    return output


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


def display_stories(stdscr, stories: Sequence[Collection]) -> Collection or None:
    """
    Display a list of stories and let the user choose one to read.
    :param stories: A list of dict objects where each dict has 'title' and 'content'.
    """
    # Display the list of titles
    for idx, story in enumerate(stories, 1):
        stdscr.addstr(f"{idx}. {story.name}\n")

    # Get user choice
    stdscr.addstr("\nChoose a story number to read (or 0 to exit): ")
    choice = int(stdscr.getkey())
    stdscr.addstr(str(choice))
    stdscr.getkey()

    # Validate the choice
    while choice < 0 or choice > len(stories):
        stdscr.addstr("\nInvalid choice. Please try again.\n")
        stdscr.addstr("\nChoose a story number to read (or 0 to exit): ")
        choice = int(stdscr.getkey())
        stdscr.addstr(str(choice))
        stdscr.getkey()

    # Display the chosen story
    if choice == 0:
        return None
    else:
        return stories[choice-1]


def main(stdscr):
    current_stories = client.list_collections()
    stdscr.clear()
    stdscr.addstr("Welcome to Story Traveler!\n")

    if current_stories and len(current_stories) > 0:
        stdscr.addstr("\nCurrent stories:\n\n")
        selected_collection = display_stories(stdscr, current_stories)
        if selected_collection:
            stdscr.clear()
            stdscr.addstr(f"{selected_collection.name} has been selected\n")
            story_settings = get_story_settings(selected_collection.name)
            if story_settings["synopsis"] == "":
                stdscr.addstr("Let's create a synopsis for this story\n")
                new_synopsis = prompt_for_story_synopsis(stdscr,
                                                         selected_collection, story_settings["storyTitle"])
                try:
                    stdscr.addstr(f"Your synopsis: {new_synopsis}\n")
                except curses.error:
                    pass
    else:
        stdscr.addstr("No stories currently exist")
        # create_new_story()

    stdscr.refresh()
    stdscr.getch()


if __name__ == "__main__":
    wrapper(main)
