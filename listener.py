from dotenv import load_dotenv
import speech_recognition as sr
from typing import Tuple
import os

load_dotenv()  # take environment variables from .env.

# Code of your application, which uses environment variables (e.g. from `os.environ` or
# `os.getenv`) as if they came from the actual environment.

openai_api_key = os.getenv("OPENAI_API_KEY")


def listen() -> Tuple[bool, str]:
    whisper_text = "failed to gather audio"
    audio_gathered = False
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            audio = r.listen(source, phrase_time_limit=20)
            # Recognize speech using whisper
            try:
                whisper_text = r.recognize_whisper(
                    audio, language="english")
            except sr.UnknownValueError:
                return (False, "UnknownValue Error")
            except sr.RequestError as e:
                return (False, "Request Error")

            if whisper_text != None and whisper_text != "":
                audio_gathered = True

    except sr.WaitTimeoutError:
        return (False, "Timeout Error")

    return (audio_gathered, whisper_text)
