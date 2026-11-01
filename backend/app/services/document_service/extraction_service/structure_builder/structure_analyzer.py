import os

from google import genai
from dotenv import load_dotenv
from pathlib import Path

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

    structure = DocumentStructure.model_validate_json(output_text)

    # Save the detected structure for testing.
    output_file = Path("document_structure.json")
    output_file.write_text(
        structure.model_dump_json(indent=2),
        encoding="utf-8",
    )

    return structure



def number_lines(text: str) -> str:
    lines = text.splitlines(keepends=True)

    numbered_lines: list[str] = []
    
    for number, line in enumerate(lines, start=1):
        numbered_lines.append(
            f"[L{number:05d}] {line}"
        )
        
    numbered_text = "".join(numbered_lines)
        
    # output_dir = Path("debug_output")
    # output_dir.mkdir(parents=True, exist_ok=True)

    # output_file = output_dir / "numbered_canonical_text.txt"
    # output_file.write_text(
    #     numbered_text,
    #     encoding="utf-8",
    # )
    
    # print(f"Numbered Canoical text written to : {output_file} ")
        

    return numbered_text