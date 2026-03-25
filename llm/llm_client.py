# llm/llm_client.py

import base64
import mimetypes
from pathlib import Path

from openai import OpenAI

from config.llm_config import OPENAI_API_KEY, OPENAI_MODEL, validate_llm_config


validate_llm_config()
client = OpenAI(api_key=OPENAI_API_KEY)


def _extract_output_text(response) -> str:
    """
    Ambil output_text dari response dengan aman.
    """
    output_text = getattr(response, "output_text", None)

    if not output_text or not str(output_text).strip():
        return ""

    return str(output_text).strip()


def _guess_mime_type(image_path: str) -> str:
    """
    Tebak MIME type berdasarkan nama file.
    Fallback ke image/jpeg kalau gak kebaca.
    """
    mime_type, _ = mimetypes.guess_type(image_path)
    return mime_type or "image/jpeg"


def generate_response(prompt: str) -> str:
    """
    Mode text biasa.
    Nerima final prompt string dan balikin text response.
    """
    if not prompt or not prompt.strip():
        return "Prompt kosong bro, gua gak bisa mikir dari kehampaan 😵"

    try:
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=prompt.strip(),
            truncation="auto",
        )

        output_text = _extract_output_text(response)

        if not output_text:
            return "Model gak ngasih output yang kebaca bro 😵"

        return output_text

    except Exception as e:
        return f"Gagal generate response dari model: {str(e)}"


def generate_file_response(prompt: str) -> str:
    """
    Mode file text-only.
    Cocok buat PDF/TXT hasil parser.
    """
    return generate_response(prompt)


def generate_image_response(prompt: str, image_path: str) -> str:
    """
    Mode multimodal untuk gambar.
    Kirim prompt + image ke model vision-capable.
    """
    if not prompt or not prompt.strip():
        return "Prompt analisis gambar kosong bro 😵"

    if not image_path or not str(image_path).strip():
        return "Path gambar kosong bro 😵"

    path = Path(image_path)

    if not path.exists():
        return f"File gambar gak ketemu bro: {image_path}"

    try:
        with open(path, "rb") as image_file:
            image_bytes = image_file.read()

        if not image_bytes:
            return "File gambar kosong bro 😵"

        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        mime_type = _guess_mime_type(str(path))

        response = client.responses.create(
            model=OPENAI_MODEL,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt.strip(),
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:{mime_type};base64,{image_b64}",
                            "detail": "auto",
                        },
                    ],
                }
            ],
            truncation="auto",
        )

        output_text = _extract_output_text(response)

        if not output_text:
            return "Model vision gak ngasih output yang kebaca bro 😵"

        return output_text

    except Exception as e:
        return f"Gagal analisis gambar dari model: {str(e)}"