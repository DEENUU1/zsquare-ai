import base64
import streamlit as st
from sqlalchemy.orm import Session

from models.user import User
from services.transcription import whisper_stt
from services.chat import get_chat_response
from repositories.client_repository import get_clients
from repositories.form_repository import get_forms_by_client
from repositories.message_repository import create_message, get_messages_by_form_id
from schemas.message_schema import MessageInputSchema
from services.report import generate_report
from utils.setup import setup
from repositories.report_repository import get_report_by_form_id
from services.text_to_audio import text_to_audio, get_html_audio
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

logger, db = setup()

# Authentication settings
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user():
    token = st.session_state.get('access_token')
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None
    user = get_user_by_email(db, email)
    return user


def login_page():
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = get_user_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            st.error("Invalid email or password")
        elif not user.is_active:
            st.error("User is inactive")
        else:
            access_token = create_access_token(data={"sub": user.email})
            st.session_state['access_token'] = access_token
            st.success("Login successful!")
            st.experimental_rerun()


def logout():
    if st.sidebar.button("Logout"):
        del st.session_state['access_token']
        st.experimental_rerun()


def init_session_state():
    if 'selected_form' not in st.session_state:
        st.session_state.selected_form = None
    if 'full_name' not in st.session_state:
        st.session_state.full_name = ""
    if 'selected_client' not in st.session_state:
        st.session_state.selected_client = None
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    if 'recording' not in st.session_state:
        st.session_state.recording = False


def sidebar():
    with st.sidebar:
        st.session_state.full_name = st.text_input("Imię i nazwisko", value=st.session_state.full_name)
        clients = get_clients(db, st.session_state.full_name)
        for client in clients:
            if st.button(client.full_name):
                st.session_state.selected_client = client
                st.session_state.selected_form = None
                st.session_state['messages'] = []
        logout()


def main_content():
    if st.session_state.selected_client:
        st.title(st.session_state.selected_client.full_name)
        col1, col2, col3 = st.columns(3)

        forms = get_forms_by_client(db, st.session_state.selected_client.id)
        form_options = [f"{form.id} - {str(form.created_at)[:10]}" for form in forms]
        selected_option = st.selectbox("Wybierz formularz:", form_options)

        if selected_option:
            selected_form = next(
                form for form in forms if f"{form.id} - {str(form.created_at)[:10]}" == selected_option)
            if selected_form != st.session_state.selected_form:
                st.session_state.selected_form = selected_form
                st.session_state['messages'] = []

            with col1:
                if st.button("Dane klienta"):
                    st.session_state.form_id_for_client_data = st.session_state.selected_form.id
                    st.switch_page("pages/client_data.py")

        if st.session_state.selected_form:
            chat_interface()

            with col2:
                report = get_report_by_form_id(db, st.session_state.selected_form.id)
                if report and report.report_content:
                    report_content = base64.b64decode(report.report_content)
                    st.download_button(
                        label="Pobierz raport",
                        data=report_content,
                        file_name="report.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.download_button(
                        label="Pobierz raport",
                        data="",
                        file_name="report.pdf",
                        mime="application/pdf",
                        disabled=True
                    )

            with col3:
                if st.button("Generuj raport"):
                    generate_report(db, st.session_state.selected_form.id)


def chat_interface():
    if not st.session_state['messages']:
        initialize_chat()

    text = whisper_stt(language='pl', start_prompt="Nagrywaj", stop_prompt="Zakończ", key="chat_input")
    if text:
        logger.info(f"Transcription: {text}")

    display_chat_messages()

    prompt = st.chat_input() or text

    if prompt:
        process_user_input(prompt)


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

    text_to_audio(ai_response)

    audio_html = get_html_audio()
    if audio_html:
        st.components.v1.html(audio_html, height=0)


def main():
    if 'access_token' not in st.session_state:
        login_page()
    else:
        user = get_current_user()
        if user:
            init_session_state()
            sidebar()
            main_content()
        else:
            st.warning("Your session has expired. Please log in again.")
            login_page()


if __name__ == "__main__":
    main()
