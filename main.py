import streamlit as st
import logging
from transcription import whisper_stt
from chat import get_chat_response
from database import get_db
from repo import get_clients, get_forms_by_client, create_message, get_messages_by_form_id
from schemas import MessageInputSchema, FormOutputSchema, ClientOutputSchema
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

if 'messages' not in st.session_state:
    st.session_state['messages'] = []


@st.experimental_dialog("Formularz")
def form(data: FormOutputSchema):
    st.write("Dane z formularza użytkownika")
    st.write(f"ID: {data.id}")
    st.write(f"Bike: {data.bike}")
    st.write(f"Boots: {data.boots}")
    st.write(f"Insoles: {data.insoles}")
    st.write(f"Pedals: {data.pedals}")
    st.write(f"Other Bikes: {data.other_bikes}")
    st.write(f"Tool Annotation: {data.tool_annotation}")
    st.write(f"Sport History: {data.sport_history}")
    st.write(f"Sport Annotation: {data.sport_annotation}")
    st.write(f"Position Problem: {data.position_problem}")
    st.write(f"Adnotation Position Problem: {data.adnotation_position_problem}")
    st.write(f"Years Cycling: {data.years_cycling}")
    st.write(f"Annual Mileage: {data.annual_mileage}")
    st.write(f"Weekly Rides: {data.weekly_rides}")
    st.write(f"Session Duration: {data.session_duration}")
    st.write(f"Participated in Races: {data.participated_in_races}")
    st.write(f"Best Results: {data.best_results}")
    st.write(f"Intensity Measurement: {data.intensity_measurement}")
    st.write(f"Other Sports: {data.other_sports}")
    st.write(f"Bike Confidence: {data.bike_confidence}")
    st.write(f"Gear Changing: {data.gear_changing}")
    st.write(f"Autumn Winter Riding: {data.autumn_winter_riding}")
    st.write(f"Preferred Grip: {data.preferred_grip}")
    st.write(f"Cadence Comfort: {data.cadence_comfort}")
    st.write(f"Group Riding Skills: {data.group_riding_skills}")
    st.write(f"Cornering Style: {data.cornering_style}")
    st.write(f"Brake Usage: {data.brake_usage}")
    st.write(f"Tire Pressure Check: {data.tire_pressure_check}")
    st.write(f"Injuries: {data.injuries}")
    st.write(f"Injuries During Cycling: {data.injuries_during_cycling}")
    st.write(f"Client ID: {data.client_id}")
    st.write(f"Created At: {data.created_at}")
    st.write(f"Updated At: {data.updated_at}")


@st.experimental_dialog("Klient")
def client(data: ClientOutputSchema):
    st.write(f"Imię i nazwisko: {data.full_name}")
    st.write(f"Data urodzenia: {data.birth_date}")
    st.write(f"Miejsce zamieszkania: {data.location}")
    st.write(f"Numer telefonu: {data.phone}")
    st.write(f"Adres email: {data.email}")


with st.sidebar:
    st.session_state.full_name = st.text_input("Imię i nazwisko", value=st.session_state.full_name)

    clients = get_clients(db, st.session_state.full_name)

    for client in clients:
        if st.button(client.full_name):
            selected_client = client
            st.session_state.selected_client = selected_client
            st.session_state.selected_form = None
            st.session_state['messages'] = []

if st.session_state.selected_client:
    st.title(st.session_state.selected_client.full_name)

    col1, col2 = st.columns(2)
    with col1:
        if "client_modal" not in st.session_state:
            if st.button("Klient"):
                client(st.session_state.selected_client)

    forms = get_forms_by_client(db, st.session_state.selected_client.id)
    form_options = [f"{form.id} - {str(form.created_at)[:10]}" for form in forms]
    selected_option = st.selectbox("Wybierz formularz:", form_options)
    if selected_option:
        selected_form = next(form for form in forms if f"{form.id} - {str(form.created_at)[:10]}" == selected_option)
        if selected_form != st.session_state.selected_form:
            st.session_state.selected_form = selected_form
            st.session_state['messages'] = []

        with col2:
            if "form_modal" not in st.session_state:
                if st.button("Formularz"):
                    form(st.session_state.selected_form)

if st.session_state.selected_form:
    if not st.session_state['messages']:
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

        ai_response = get_chat_response(st.session_state["messages"])
        st.session_state["messages"].append({"role": "assistant", "content": ai_response})
        st.chat_message("assistant").write(ai_response)

        create_message(db, MessageInputSchema(
            role="assistant",
            text=ai_response,
            form_id=st.session_state.selected_form.id
        ))
