import streamlit as st
from ai.transcription import whisper_stt
from ai.chat import get_chat_response
from repositories.client_repository import get_clients
from repositories.form_repository import get_forms_by_client
from repositories.message_repository import create_message, get_messages_by_form_id
from schemas.message_schema import MessageInputSchema
from schemas.form_schema import FormOutputSchema
from schemas.client_schema import ClientOutputSchema
from services.report import generate_report
from utils.setup import setup

logger, db = setup()


def init_session_state():
    if 'selected_form' not in st.session_state:
        st.session_state.selected_form = None
    if 'full_name' not in st.session_state:
        st.session_state.full_name = ""
    if 'selected_client' not in st.session_state:
        st.session_state.selected_client = None
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []


init_session_state()


@st.experimental_dialog("Formularz")
def form_dialog(data: FormOutputSchema):
    st.write("Dane z formularza użytkownika")
    for field, value in data.__dict__.items():
        st.write(f"{field.capitalize()}: {value}")


@st.experimental_dialog("Klient")
def client_dialog(data: ClientOutputSchema):
    fields = ["full_name", "birth_date", "location", "phone", "email"]
    for field in fields:
        st.write(f"{field.capitalize().replace('_', ' ')}: {getattr(data, field)}")


def sidebar():
    with st.sidebar:
        st.session_state.full_name = st.text_input("Imię i nazwisko", value=st.session_state.full_name)
        clients = get_clients(db, st.session_state.full_name)
        for client in clients:
            if st.button(client.full_name):
                st.session_state.selected_client = client
                st.session_state.selected_form = None
                st.session_state['messages'] = []


def main_content():
    if st.session_state.selected_client:
        st.title(st.session_state.selected_client.full_name)
        col1, col2 = st.columns(2)
        with col1:
            if "client_modal" not in st.session_state and st.button("Klient"):
                client_dialog(st.session_state.selected_client)

        forms = get_forms_by_client(db, st.session_state.selected_client.id)
        form_options = [f"{form.id} - {str(form.created_at)[:10]}" for form in forms]
        selected_option = st.selectbox("Wybierz formularz:", form_options)

        if selected_option:
            selected_form = next(
                form for form in forms if f"{form.id} - {str(form.created_at)[:10]}" == selected_option)
            if selected_form != st.session_state.selected_form:
                st.session_state.selected_form = selected_form
                st.session_state['messages'] = []

            with col2:
                if "form_modal" not in st.session_state and st.button("Formularz"):
                    form_dialog(st.session_state.selected_form)

        if st.session_state.selected_form:
            chat_interface()


def chat_interface():
    if not st.session_state['messages']:
        initialize_chat()

    text = whisper_stt(language='en', start_prompt="Nagrywaj", stop_prompt="Zakończ", key="chat_input")
    if text:
        logger.info(f"Transcription: {text}")

    display_chat_messages()

    prompt = st.chat_input() or text

    if prompt:
        process_user_input(prompt)

    if st.button("Generuj raport"):
        generate_report(db, st.session_state.selected_form.id)


def initialize_chat():
    initial_messages = get_messages_by_form_id(db, st.session_state.selected_form.id)
    st.session_state["messages"] = [{"role": msg.role, "content": msg.text} for msg in initial_messages]

    if len(st.session_state["messages"]) == 0 or st.session_state["messages"][0]["role"] != "assistant":
        initial_assistant_message = {
            "role": "assistant",
            "content": "Proszę podać wzrost klienta."
        }
        st.session_state["messages"].insert(0, initial_assistant_message)


def display_chat_messages():
    for msg in st.session_state["messages"]:
        st.chat_message(msg["role"]).write(msg["content"])


def process_user_input(prompt):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    create_message(
        db, MessageInputSchema(role="user", text=prompt, form_id=st.session_state.selected_form.id)
    )
    st.chat_message("user").write(prompt)

    ai_response = get_chat_response(st.session_state["messages"])
    st.session_state["messages"].append({"role": "assistant", "content": ai_response})
    st.chat_message("assistant").write(ai_response)

    create_message(
        db, MessageInputSchema(
            role="assistant", text=ai_response, form_id=st.session_state.selected_form.id
        )
    )


def main():
    sidebar()
    main_content()


if __name__ == "__main__":
    main()
