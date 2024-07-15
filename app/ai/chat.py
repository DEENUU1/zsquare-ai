from typing import List, Dict

from openai import OpenAI

from config.settings import settings


def get_chat_response(messages: List[Dict[str, str]]) -> str:
    if not settings.OPENAI_APIKEY:
        raise ValueError("OPENAI_APIKEY is not set")

    system_prompt = """
    ## Important
    !!!You need to answer write in Polish language!!!

    you are the assistant of a "fitter" who interviews a customer about a bicycle, 
    the "fitter" must collect the appropriate data. 
    Ask the "fitter" one by one about the appropriate data according to the scenario given below, 
    what data it needs to collect. 

    ## Important
    "Fitter" can also provide data in a different order, 
    so you need to pay attention to what you are asking about

    ## Data to collect
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
    6. Profil otropedyczny/zdrowotny - HERE ASK ABOUT ANY MEDICAL CONDITIONS
    7. Profil motoryczny/ocena fizjoterapeutyczna 
    8. Adnotacje dotyczące profilu motorycznego/oceny fizjoterapeutycznej
    9. Wymiary roweru (tutaj zapytaj krok po kroku o każdy wymiar)
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

    system_message = {"role": "system", "content": system_prompt}

    messages = [system_message] + messages

    try:
        client = OpenAI(api_key=settings.OPENAI_APIKEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        if not response:
            return "No response from OpenAI API :("
        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"
