import chromadb
from listener import main

from chromadb.config import Settings
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="data"
))


if __name__ == "__main__":
    main(device="avfoundation", src=":1")
