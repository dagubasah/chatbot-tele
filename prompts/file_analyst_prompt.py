# prompts/file_analysis_prompt.py

def build_file_analysis_prompt(
    extracted_text: str,
    user_question: str = "",
    file_type: str = "file",
    file_name: str = "unknown",
) -> str:
    """
    Bangun prompt analisis file/gambar untuk LLM.

    Parameters:
        extracted_text: hasil parsing dokumen/gambar dalam bentuk teks
        user_question: pertanyaan / caption dari user
        file_type: document / image / file
        file_name: nama file asli

    Returns:
        Prompt final string
    """

    cleaned_text = (extracted_text or "").strip()
    cleaned_question = (user_question or "").strip()

    if not cleaned_text:
        cleaned_text = "[Tidak ada konten yang berhasil diekstrak dari file.]"

    if not cleaned_question:
        cleaned_question = "Jelaskan isi file ini secara ringkas dan jelas."

    return f"""
Kamu adalah analis file yang cermat, jelas, dan tidak mengada-ada.

Tugas kamu:
- pahami isi file berdasarkan teks hasil ekstraksi
- jawab pertanyaan user hanya berdasarkan konteks yang tersedia
- kalau informasi tidak cukup, bilang dengan jujur
- kalau user tidak bertanya spesifik, berikan ringkasan yang padat
- kalau file berisi data penting, tampilkan poin-poin utamanya
- jangan halusinasi atau mengarang isi yang tidak ada di file

Informasi file:
- Tipe file: {file_type}
- Nama file: {file_name}

Pertanyaan user:
{cleaned_question}

Konten hasil ekstraksi:
\"\"\"
{cleaned_text}
\"\"\"

Sekarang berikan jawaban terbaik dalam bahasa Indonesia yang natural, jelas, dan langsung ke inti.
""".strip()