import streamlit as st
import logging
from transcription import whisper_stt
from chat import get_ai_response
from database import get_db
from repo import get_clients, get_forms_by_client, create_message, get_messages_by_form_id
from schemas import MessageInputSchema
from utils import init_db


def setup():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    init_db()
    return logger, next(get_db())


logger, db = setup()

if 'selected_form' not in st.session_state:
    st.session_state.selected_form = None

if 'full_name' not in st.session_state:
    st.session_state.full_name = ""

if 'selected_client' not in st.session_state:
    st.session_state.selected_client = None

with st.sidebar:
    st.markdown("[Github](https://github.com/DEENUU1)")

    st.session_state.full_name = st.text_input("Full name", value=st.session_state.full_name)

    clients = get_clients(db, st.session_state.full_name)

    for client in clients:
        if st.button(client.full_name):
            st.session_state.selected_client = client
            st.session_state.selected_form = None

if st.session_state.selected_client:
    st.title(f"💬 Chatbot: {st.session_state.selected_client.full_name}")

    forms = get_forms_by_client(db, st.session_state.selected_client.id)

    st.subheader("Formularze")
    for form in forms:
        if st.button(f"{form.id} - {str(form.created_at)[:10]}"):
            st.session_state.selected_form = form

else:
    st.title("💬 Chatbot")

if st.session_state.selected_form:
    if "messages" not in st.session_state:
        initial_messages = get_messages_by_form_id(db, st.session_state.selected_form.id)
        st.session_state["messages"] = [{"role": msg.role, "content": msg.text} for msg in initial_messages]

        if len(st.session_state["messages"]) == 0 or st.session_state["messages"][0]["role"] != "assistant":
            initial_assistant_message = {
                "role": "assistant",
                "content": "Proszę podać wzrost klienta."
            }
            st.session_state["messages"].insert(0, initial_assistant_message)

    text = whisper_stt(
        language='en',
        start_prompt="Nagrywaj",
        stop_prompt="Zakończ",
        key="chat_input"
    )
    if text:
        logger.info(f"Transcription: {text}")

    for msg in st.session_state["messages"]:
        st.chat_message(msg["role"]).write(msg["content"])

    prompt = st.chat_input() or text

    if prompt:
        st.session_state["messages"].append({"role": "user", "content": prompt})

        create_message(db, MessageInputSchema(
            role="user",
            text=prompt,
            form_id=st.session_state.selected_form.id
        ))

        st.chat_message("user").write(prompt)

        ai_response = get_ai_response(st.session_state["messages"])
        st.session_state["messages"].append({"role": "assistant", "content": ai_response})
        st.chat_message("assistant").write(ai_response)

        create_message(db, MessageInputSchema(
            role="assistant",
            text=ai_response,
            form_id=st.session_state.selected_form.id
        ))
