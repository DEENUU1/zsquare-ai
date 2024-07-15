from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
import io
from reportlab.pdfbase.ttfonts import TTFont
from typing import List, Any
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from sqlalchemy.orm import Session
from repositories.client_repository import get_client_by_id
from repositories.form_repository import get_form_by_id
from repositories.message_repository import get_messages_by_form_id
from schemas.form_schema import FormOutputSchema
from utils.filename_generator import generate_filename


class Report:
    @staticmethod
    def add_spaces(elements, height=7):
        elements.append(Spacer(1, height))

    @staticmethod
    def add_text(elements: List, style, text: str) -> None:
        elements.append(Paragraph(text, style))

    @staticmethod
    def get_paragraph_style() -> Any:
        paragraph_style = ParagraphStyle('services_description')
        paragraph_style.fontName = 'Abhaya'
        paragraph_style.fontSize = 8
        paragraph_style.bold = False
        return paragraph_style

    @staticmethod
    def get_header_style() -> Any:
        header_style = ParagraphStyle('header')
        header_style.fontName = 'Abhaya'
        header_style.fontSize = 10
        header_style.bold = True
        return header_style

    def generate_pdf_report(
            self,
            form_data: FormOutputSchema,
            structured_output: dict,
            summary: str,
    ) -> io.BytesIO:
        style = self.get_paragraph_style()
        header_style = self.get_header_style()

        buffer = io.BytesIO()
        pdfmetrics.registerFont(TTFont("Abhaya", "Abhaya.ttf"))
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        self.add_text(elements, header_style, "Form Data")
        for field, value in form_data.dict().items():
            self.add_text(elements, style, f"{field}: {value}")
            self.add_spaces(elements)

        self.add_spaces(elements, height=14)

        self.add_text(elements, header_style, "Structured Output")
        for key, value in structured_output.items():
            self.add_text(elements, style, f"{key}: {value}")
            self.add_spaces(elements)

        self.add_spaces(elements, height=14)

        self.add_text(elements, header_style, "Summary")
        self.add_text(elements, style, summary)

        doc.build(elements)
        buffer.seek(0)

        return buffer


def generate_report(db: Session, form_id: int = 1) -> None:
    form_data = get_form_by_id(db, form_id)
    client_data = get_client_by_id(db, form_data.client_id)
    messages = get_messages_by_form_id(db, form_id)

    filename = generate_filename(form_data, client_data)

    # structured_output = get_conversation_information(messages)
    # print(structured_output)
    structured_output = {
        'anthropometry': {
            'body_height': 190,
            'sternum_handle': 20,
            'inner_leg_length': 30,
            'shoulder_width': 120,
            'arm_span': 13
        },
        'anthropometry_notes': 'nie',
        'sports_history': 'nie',
        'sports_history_notes': '',
        'position_problems': 'nie',
        'position_problems_notes': 'nie',
        'orthopedic_profile': 'nie',
        'motor_profile': 'nie',
        'motor_profile_notes': 'nie',
        'bicycle_dimensions': {
            'saddle_height': 12,
            'saddle_model': 'shimano',
            'saddle_size': '30cm',
            'saddle_tilt': 12,
            'seatpost_offset': 11,
            'saddle_to_bottom_bracket': 111,
            'saddle_to_handlebar_center': 21,
            'saddle_to_shifter': 24,
            'height_difference': 90,
            'stem_length': 35,
            'stem_angle': None,
            'handlebar_width': 120,
            'handlebar_model': 'shimano xyz',
            'spacer_height': 97,
            'crank_length': 71,
            'shifter_angle': 18
        },
        'bicycle_dimensions_notes': 'nie'
    }
    # summary = generate_session_summary(form_data, structured_output)
    # print(summary)
    summary = (
        "Na podstawie danych klienta oraz przeprowadzonych sesji bikefittingu, "
        "wprowadzono następujące zmiany w ustawieniach roweru:\n\n"
        "1. Siodełko zostało obniżone o 7 mm, a kąt pochylenia zwiększony do -2 stopni.\n"
        "2. Pozycja kierownicy pozostała bez zmian.\n"
        "3. Mostek został wydłużony o 1 cm.\n"
        "4. Przesunięto siodełko o 6 mm ku tyłowi w celu przeniesienia środka ciężkości.\n"
        "5. Podkładka pod mostkiem została obniżona o 20 mm.\n"
        "6. Zmieniono pedały na model SPD 540.\n"
        "7. Zalecono klientowi ćwiczenia redukujące napięcia, regularne jazdy w stójce, zmiany chwytów oraz kontrolę łokci.\n"
        "8. Zalecono wzmocnienie treningiem siłowym obręczy barkowej i pleców.\n\n"
        "Dzięki powyższym dostosowaniom, zmniejszono napięcia mięśniowe, poprawiono stabilność i komfort jazdy klienta na rowerze."
    )

    buffer = Report().generate_pdf_report(form_data, structured_output, summary)

    with open(f"reports/{filename}", "wb") as f:
        f.write(buffer.getbuffer())

    return
