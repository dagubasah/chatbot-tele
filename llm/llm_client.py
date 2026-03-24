# llm/llm_client.py

from openai import OpenAI

from config.llm_config import OPENAI_API_KEY, OPENAI_MODEL, validate_llm_config


validate_llm_config()
client = OpenAI(api_key=OPENAI_API_KEY)


def generate_response(prompt: str) -> str:
    """
    Kirim prompt final ke model dan balikin hasil text.
    """
    if not prompt or not prompt.strip():
        return "Prompt kosong bro, gua gak bisa mikir dari kehampaan 😵"

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=prompt
    )

    return response.output_text.strip()