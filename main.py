from dotenv import load_dotenv
from chromadb.config import Settings
import os
import chromadb
from chromadb.utils import embedding_functions
import openai
import uuid

from utils import synopsis_explanation

# Load your API key from an environment variable or secret management service
openai.api_key = os.getenv("OPENAI_API_KEY")


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


def prompt_for_story_outline(story_name: str):
    # Prompt openai for story outline using embeddings
    # TODO: Implement
    return ""


def prompt_for_story_synopsis(story_name: str):
    # Prompt openai for story outline using embeddings
    story_name = story_name.replace("_", " ").lower()
    collection = client.get_collection(
        name=story_name, embedding_function=openai_ef)

    # Ask for story synopsis
    print(f"Enter a story synopsis: \n {synopsis_explanation}")
    user_input = input("Enter a story synopsis: ")

    return ""


def get_embedding(text, model="text-embedding-ada-002"):
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
        # print(new_collection.peek())


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


# Have a collection of stories which then lead to a specific collection with documents pertaining to that story


if __name__ == "__main__":
    delete_story()
    current_stories = client.list_collections()
    if current_stories and len(current_stories) > 0:
        print("Current stories:")
        for story in current_stories:
            print(story.name)
    else:
        print("No stories currently exist")
        create_new_story()
