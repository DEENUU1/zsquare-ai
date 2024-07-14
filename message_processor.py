import logging
import os
from typing import Any, Optional, List

from langchain.chains import TransformChain
from langchain_core.exceptions import OutputParserException
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import chain
from langchain_openai import ChatOpenAI
from repo import get_messages_by_form_id
from database import get_db
from config import settings
from schemas import MessageOutputSchema

os.environ["OPENAI_API_KEY"] = settings.OPENAI_APIKEY

logger = logging.getLogger(__name__)


class Antropometria(BaseModel):
    wysokosc_ciala: float = Field(..., description="Wysokość ciała w centymetrach")
    rekojeść_mostka: float = Field(..., description="Długość rękojeści mostka / długość tułowia w centymetrach")
    dlugosc_wewnetrzna_nogi: float = Field(..., description="Długość wewnętrzna nogi w centymetrach")
    szerokosc_ramion: float = Field(..., description="Szerokość ramion w centymetrach")
    zasieg_ramion: float = Field(..., description="Zasięg ramion w centymetrach")


class WymiaryRoweru(BaseModel):
    wysokosc_siodla: Optional[float] = Field(None, description="Wysokość siodła w centymetrach")
    model_siodla: Optional[str] = Field(None, description="Model siodła")
    rozmiar_siodla: Optional[str] = Field(None, description="Rozmiar siodła")
    nachylenie_siodla: Optional[float] = Field(None, description="Nachylenie siodła w stopniach")
    offset_sztycy: Optional[float] = Field(None, description="Offset sztycy w milimetrach")
    odsuniecie_siodla_od_osi_suportu: Optional[float] = Field(None,
                                                              description="Odsunięcie siodła od osi suportu w centymetrach")
    koncowka_siodla_od_srodka_kierownicy: Optional[float] = Field(None,
                                                                  description="Odległość końcówki siodła od środka kierownicy w centymetrach")
    koncowka_siodla_do_manetki: Optional[float] = Field(None,
                                                        description="Odległość końcówki siodła do manetki w centymetrach")
    roznica_wysokosci: Optional[float] = Field(None, description="Różnica wysokości (DROP) w centymetrach")
    mostek_dlugosc: Optional[float] = Field(None, description="Długość mostka w milimetrach")
    mostek_kat: Optional[float] = Field(None, description="Kąt mostka w stopniach")
    szerokosc_kierownicy: Optional[float] = Field(None, description="Szerokość kierownicy w centymetrach")
    model_kierownicy: Optional[str] = Field(None, description="Model kierownicy")
    wysokosc_podkladek: Optional[float] = Field(None, description="Wysokość podkładek w milimetrach")
    dlugosc_korby: Optional[float] = Field(None, description="Długość korby w milimetrach")
    kat_manetek: Optional[float] = Field(None, description="Kąt manetek (kierownica / dźwignia) w stopniach")


class ConversationInformation(BaseModel):
    tag_on: bool = Field(
        ...,
        example=True,
        description="Set to True if image contains tag else return False.",
    )
    color: str = Field(
        ...,
        example="red",
        description="The color of the paper in the image. "
                    "Possible values are: 'red', 'yellow', 'green', or 'none' "
                    "if no paper is detected.",
    )
    antropometria: Antropometria = Field(
        ...,
        description="Antropometria zawierająca szczegółowe pomiary",
    )
    adnotacje_antropometria: str = Field(..., description="Adnotacje dotyczące antropometrii")
    historia_sportowa: str = Field(..., description="Historia sportowa")
    adnotacje_historia_sportowa: str = Field(..., description="Adnotacja dotycząca historii sportowej")
    problemy_z_pozycja: str = Field(..., description="Obecne problemy z pozycją na rowerze")
    adnotacje_problemy_z_pozycja: str = Field(..., description="Adnotacja dotycząca problemów z pozycją na rowerze")
    profil_ortopedyczny: str = Field(..., description="Profil ortopedyczny/zdrowotny")
    profil_motoryczny: str = Field(..., description="Profil motoryczny/ocena fizjoterapeutyczna")
    adnotacje_profil_motoryczny: str = Field(...,
                                             description="Adnotacje dotyczące profilu motorycznego/oceny fizjoterapeutycznej")
    wymiary_roweru: WymiaryRoweru = Field(..., description="Szczegółowe wymiary roweru")
    adnotacje_wymiary_roweru: str = Field(..., description="Adnotacje dotyczące wymiarów roweru")


parser = JsonOutputParser(pydantic_object=ConversationInformation)


def load_messages(inputs: dict) -> dict:
    return {"messages": inputs["message_dict"]}


load_message_chain = TransformChain(
    input_variables=["message_dict"],
    output_variables=["messages"],
    transform=load_messages
)


@chain
def conversation_model(inputs: dict) -> str | list[str | dict[Any, Any]]:
    model: ChatOpenAI = ChatOpenAI(
        temperature=0.5,
        model="gpt-4",
        max_tokens=1024,
    )
    msg = model.invoke(
        [
            HumanMessage(
                content=[
                    {"type": "text", "text": inputs["prompt"]},
                    {"type": "text", "text": parser.get_format_instructions()},
                    {"type": "text", "text": str(inputs['messages'])},
                ]
            )
        ]
    )
    logger.info(f"Model response: {msg.content}")
    return msg.content


def convert_messages_to_dict(messages: List[MessageOutputSchema]) -> list[dict]:
    conversation = []

    for message in messages:
        conversation.append(
            {"role": message.role, "content": message.text}
        )

    return conversation


def get_conversation_information(form_id: int) -> Optional[dict]:
    vision_prompt = """
    Process conversation and return structured output based on the given schema.
    Collect the following data:
    1. Antropometria
    - wysokość ciała
    - rękojeść mostka/długość tułowia
    - długość wewnętrzna nogi
    - szerokość ramion
    - zasięg ramion
    - adnotacje dotyczące antropometrii
    2. Historia sportowana
    3. Adnotacja dotycząca historii sportowej, zapytaj czy trzeba coś dodać
    4. Obecne problemy z pozycja na rowerze
    5. Adnotacja dotycząca problemów z pozycją na rowerze, zapytaj czy trzeba coś dodać
    6. Profil otropedyczny/zdrowotny - zapytaj o wszelkie schorzenia
    7. Profil motoryczny/ocena fizjoterapeutyczna 
    8. Adnotacje dotyczące profilu motorycznego/oceny fizjoterapeutycznej
    9. Wymiary roweru (zapytaj krok po kroku o każdy wymiar)
    - Wysokość siodła [Końcowe i opcjonalne]
    - Model siodła [Końcowe i opcjonalne]
    - Rozmiar siodła [Końcowe i opcjonalne]
    - Nachylenie siodła [Końcowe i opcjonalne]
    - Offset sztycy [Końcowe i opcjonalne]
    - Odsunięcie siodła od osi suportu [Końcowe i opcjonalne]
    - Końcówka siodła od środka kierownicy [Końcowe i opcjonalne]
    - Końcówka siodła do manetki [Końcowe i opcjonalne]
    - Różnica wysokości (DROP) [Końcowe i opcjonalne]
    - Mostek długość / kąt [Końcowe i opcjonalne]
    - Szerokość kierownicy [Końcowe i opcjonalne]
    - Model kierownicy [Końcowe i opcjonalne]
    - Wysokość podkładek [Końcowe i opcjonalne]
    - Długość korby [Końcowe i opcjonalne]
    - Kąt manetek (kierownica / dźwignia) [Końcowe i opcjonalne]
    10. Adnotacje dotyczące wymiarów roweru
    """
    conversation_chain = load_message_chain | conversation_model | parser

    db = next(get_db())
    messages = get_messages_by_form_id(db, form_id)
    messages_dict = convert_messages_to_dict(messages)

    try:
        return conversation_chain.invoke(
            {"message_dict": messages_dict, "prompt": vision_prompt}
        )
    except OutputParserException as e:
        logger.error(f"Failed to parse the output (OutputParserException): {e}")
        return None

    except Exception as e:
        logger.error(f"Failed to get conversation information (Unknown Exception): {e}")
        return None


if __name__ == "__main__":
    output = get_conversation_information(1)
    print(output)
