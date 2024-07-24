from typing import List, Dict
from openai import OpenAI
from config.settings import settings
import logging


logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self):
        if not settings.OPENAI_APIKEY:
            logger.error("OPENAI_APIKEY is not set")
            raise ValueError("OPENAI_APIKEY is not set")

        self.client = OpenAI(api_key=settings.OPENAI_APIKEY)

    def create_chat_completion(self, messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo") -> str:
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
            )
            if not response.choices:
                logger.error("No response from OpenAI API")
                raise ValueError("No response from OpenAI API")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in OpenAI API call: {str(e)}")
            raise ValueError(f"Error in OpenAI API call: {str(e)}")

    def convert_text_to_speech(self, input_text: str):
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=input_text,
            )
            response.stream_to_file("output.mp3")

        except Exception as e:
            logger.error(f"Error in OpenAI API call: {str(e)}")
            raise ValueError(f"Error in OpenAI API call: {str(e)}")