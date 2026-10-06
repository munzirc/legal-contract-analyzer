import os

from google import genai
from dotenv import load_dotenv

from app.schemas.llm_output_schema import DocumentStructure
from app.prompts.structure_analyzer_prompt import analyzer_prompt

load_dotenv()
    
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def detect_structure(text: str) -> DocumentStructure:
    
    numbered_text = number_lines(text)
    
    prompt = analyzer_prompt(numbered_text)
    
    interaction = client.interactions.create(
        model="gemini-3.1-flash-lite",
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": DocumentStructure.model_json_schema()
        }
    )
    
    output_text = interaction.output_text

    if output_text is None:
        raise ValueError("Gemini returned no output.")

    return DocumentStructure.model_validate_json(output_text)



def number_lines(text: str) -> str:
    lines = text.splitlines()

    numbered_lines: list[str] = []

    for number, line in enumerate(lines, start=1):
        numbered_lines.append(
            f"[L{number:05d}] {line}"
        )

    return "\n".join(numbered_lines)