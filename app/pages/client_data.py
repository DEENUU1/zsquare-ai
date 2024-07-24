import streamlit as st
from repositories.client_repository import get_client_by_id
from repositories.form_repository import get_form_by_id
from utils.setup import setup

logger, db = setup()


def get_polish_label(field_name):
    labels = {
        # Etykiety dla formularza
        'id': 'ID formularza',
        'bike': 'Rower',
        'boots': 'Buty',
        'insoles': 'Wkładki',
        'pedals': 'Pedały',
        'other_bikes': 'Inne rowery',
        'tool_annotation': 'Adnotacja narzędzia',
        'sport_history': 'Historia sportowa',
        'sport_annotation': 'Adnotacja sportowa',
        'position_problem': 'Problem z pozycją',
        'adnotation_position_problem': 'Adnotacja problemu z pozycją',
        'years_cycling': 'Lata jazdy na rowerze',
        'annual_mileage': 'Roczny przebieg',
        'weekly_rides': 'Tygodniowe przejażdżki',
        'session_duration': 'Czas trwania sesji',
        'participated_in_races': 'Udział w wyścigach',
        'best_results': 'Najlepsze wyniki',
        'intensity_measurement': 'Pomiar intensywności',
        'other_sports': 'Inne sporty',
        'bike_confidence': 'Pewność na rowerze',
        'gear_changing': 'Zmiana biegów',
        'autumn_winter_riding': 'Jazda jesienno-zimowa',
        'preferred_grip': 'Preferowany chwyt',
        'cadence_comfort': 'Komfort kadencji',
        'group_riding_skills': 'Umiejętności jazdy grupowej',
        'cornering_style': 'Styl pokonywania zakrętów',
        'brake_usage': 'Użycie hamulców',
        'tire_pressure_check': 'Kontrola ciśnienia w oponach',
        'injuries': 'Urazy',
        'injuries_during_cycling': 'Urazy podczas jazdy na rowerze',
        'client_id': 'ID klienta',

        # Etykiety dla danych klienta
        'full_name': 'Imię i nazwisko',
        'birth_date': 'Data urodzenia',
        'location': 'Lokalizacja',
        'phone': 'Telefon',
        'email': 'E-mail',

        # Wspólne etykiety
        'created_at': 'Data utworzenia',
        'updated_at': 'Data aktualizacji'
    }
    return labels.get(field_name, field_name.capitalize().replace('_', ' '))


def main():
    form_id = st.session_state.get('form_id_for_client_data')
    if form_id is not None:
        form_data = get_form_by_id(db, form_id)
        if form_data:
            client_data = get_client_by_id(db, form_data.client_id)

            st.title("Dane klienta i formularza")

            st.header("Dane klienta")
            for field, value in client_data.__dict__.items():
                if field != '_sa_instance_state':
                    st.write(f"{get_polish_label(field)}: {value}")

            st.header("Dane z formularza użytkownika")
            for field, value in form_data.__dict__.items():
                if field != '_sa_instance_state':
                    st.write(f"{get_polish_label(field)}: {value}")

        else:
            st.error("Nie znaleziono formularza o podanym ID.")
    else:
        st.error("Nie podano ID formularza.")

    if st.button("Powrót do strony głównej"):
        if 'form_id_for_client_data' in st.session_state:
            del st.session_state.form_id_for_client_data
        st.switch_page("main.py")


if __name__ == "__main__":
    main()
