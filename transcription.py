from typing import Optional

from openai import OpenAI
import streamlit as st
from streamlit_mic_recorder import mic_recorder
import io
from config import settings
import logging


logger = logging.getLogger(__name__)


def whisper_stt(
        start_prompt="Start recording",
        stop_prompt="Stop recording",
        just_once=False,
        use_container_width=False,
        language=None,
        callback=None,
        args=(),
        kwargs=None,
        key=None
) -> Optional[str]:
    if 'openai_client' not in st.session_state:
        st.session_state.openai_client = OpenAI(api_key=settings.OPENAI_APIKEY)

    if '_last_speech_to_text_transcript_id' not in st.session_state:
        st.session_state._last_speech_to_text_transcript_id = 0

    if '_last_speech_to_text_transcript' not in st.session_state:
        st.session_state._last_speech_to_text_transcript = None

    if key and key + '_output' not in st.session_state:
        st.session_state[key + '_output'] = None

    audio = mic_recorder(
        start_prompt=start_prompt,
        stop_prompt=stop_prompt,
        just_once=just_once,
        use_container_width=use_container_width,
        key=key
    )

    if audio is None:
        return None

    id = audio['id']
    new_output = (id > st.session_state._last_speech_to_text_transcript_id)

    if new_output:
        output = None
        st.session_state._last_speech_to_text_transcript_id = id
        audio_bio = io.BytesIO(audio['bytes'])
        audio_bio.name = 'audio.mp3'

        success = False
        err = 0
        while not success and err < 3:
            try:
                transcript = st.session_state.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_bio,
                    language=language
                )
                success = True
                output = transcript.text
                st.session_state._last_speech_to_text_transcript = output
            except Exception as e:
                logger.error(e)
                err += 1

        if not success:
            return None
    elif not just_once:
        output = st.session_state._last_speech_to_text_transcript
    else:
        return None

    if key:
        st.session_state[key + '_output'] = output

    if new_output and callback:
        callback(*args, **(kwargs or {}))

    return output
