import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from app.services.document_service.section_based_chunks.structure_detection.prompts import section_detection_prompt
from app.services.document_service.section_based_chunks.structure_detection.schemas import DocumentStructure

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

numbered_txt_file = Path("test_outputs/numbered_canonical_text.txt")

def detect_sections(text: str) -> DocumentStructure:
    numbered_text = number_lines(text)
    prompt = section_detection_prompt(numbered_text)

    interaction = client.interactions.create(
        model="gemini-3.1-flash-lite",
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": DocumentStructure.model_json_schema()
        },
    )

    output_text = interaction.output_text

    if not output_text:
        raise ValueError("Gemini returned no output.")

    structure = DocumentStructure.model_validate_json(output_text)

    return structure


def number_lines(text: str) -> str:
    lines = text.splitlines(keepends=True)
    
    
    numbered_text = "".join(
        f"[L{number:05d}] {line}"
        for number, line in enumerate(lines, start=1)
    )
    
    # numbered_txt_file.write_text(numbered_text, encoding="utf-8")
    # print(f"Numbered text written to file : {numbered_txt_file}")
    
    
    return numbered_text
