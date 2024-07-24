import base64
from typing import Optional

from services.openai import OpenAIClient
import os


def text_to_audio(text: str):
    client = OpenAIClient()
    client.convert_text_to_speech(text)
    return


def get_html_audio(audio_file: str = "output.mp3") -> Optional[str]:
    if not os.path.exists(audio_file):
        return None

    with open(audio_file, "rb") as f:
        audio_bytes = f.read()

    audio_base64 = base64.b64encode(audio_bytes).decode()

    audio_html = f"""
           <audio autoplay>
               <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
           </audio>
       """
    return audio_html
