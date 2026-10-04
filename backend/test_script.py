import os
import re
import json

from google import genai
from dotenv import load_dotenv

from app.services.document_service.extraction_service.extract_document import extract_document
from app.schemas.llm_output_schema import DocumentStructure

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PDF_PATH = "test_documents/test-contract-document-2.pdf"


def number_lines(text: str) -> str:
    lines = text.splitlines()

    numbered_lines = []

    for number, line in enumerate(lines, start=1):
        numbered_lines.append(
            f"[L{number:05d}] {line}"
        )

    return "\n".join(numbered_lines)


with open(PDF_PATH, "rb") as file:
    file_content = file.read()


extracted_document = extract_document(
    file_content=file_content,
    file_type="pdf"
)

numbered_text = number_lines(extracted_document.text)

print(f"Extracted characters: {len(extracted_document.text)}")
print(f"Extracted lines: {len(extracted_document.text.splitlines())}")

prompt = f"""
You are analyzing the structure of a legal contract.

Your task is to identify ONLY the top-level structural regions of the document.

A top-level region is a major organizational part of the contract that contains one or more clauses, paragraphs, or subsections.

Do NOT identify:

* Individual clauses
* Subsections
* Paragraphs
* Sentences
* Lists or bullet points
* Ordinary headings that belong to a clause or subsection
* Standalone page numbers
* Dates, addresses, names, or other metadata

Possible top-level region types include:

* PREAMBLE
* RECITALS
* ARTICLE
* SECTION
* SCHEDULE
* EXHIBIT
* APPENDIX
* ANNEX
* ANNEXURE
* SIGNATURES

These are examples, not an exhaustive list. Use the structural type that best represents the document when another clearly identifiable top-level structure exists.

Rules:

1. Identify only structures that actually exist in the document.
2. Never invent a section, article, schedule, or other structure.
3. Return the exact line number where each top-level region begins.
4. Use the line numbers provided in the document. Do not calculate or guess line numbers.
5. For numbered structures, return the number exactly as it appears in the document.
6. If a top-level region has a title, return its title.
7. If a top-level region does not have a number, set its number to null.
8. If a top-level region does not have a clear title, set its title to null.
9. Standalone page numbers are not structural regions.
10. Do not interpret every numbered item as a top-level section. For example, "1.1", "1.2", or "15.1" are normally subsections or clauses rather than top-level sections.
11. A numbered heading such as "1. PERFORMANCE OF SERVICES." can be a top-level SECTION when it clearly begins a major section of the contract.
12. An "ARTICLE 1" or "ARTICLE — 1" heading can be a top-level ARTICLE.
13. SCHEDULE, EXHIBIT, APPENDIX, ANNEX, and ANNEXURE headings can be top-level regions when they begin a distinct major part of the document.
14. A SIGNATURES section should be identified when it clearly begins the signature portion of the contract.
15. Do not identify headings merely because they are visually prominent or written in uppercase. The heading must represent a genuine top-level structural boundary.
16. Preserve the document's original structure. Do not rename, renumber, merge, or split regions unless the document itself clearly indicates that structure.

Important distinction:

For example, if the document contains:

1. PERFORMANCE OF SERVICES
   1.1 Scope
   1.2 Responsibilities
   1.3 Service Requirements

then identify only:

SECTION 1 - PERFORMANCE OF SERVICES

Do not identify 1.1, 1.2, or 1.3 as separate top-level regions.

Similarly, if the document contains:

20. INDEMNIFICATION
    20.1 General
    20.2 Limitations
    20.3 Exceptions

identify only Section 20.

The goal is to reconstruct the document's major structural hierarchy, not to identify every heading.

The document below has been numbered line-by-line. Use those line numbers when identifying the start of each top-level region.

Here is the document:

{numbered_text}

"""

interaction = client.interactions.create(
    model="gemini-3.1-flash-lite",
    input=prompt,
    response_format={
        "type": "text",
        "mime_type": "application/json",
        "schema": DocumentStructure.model_json_schema()
    }
)

result = DocumentStructure.model_validate_json(
    interaction.output_text
)

print("\n")
print("=" * 80)
print("GEMINI STRUCTURE RESULT")
print("=" * 80)

lines = extracted_document.text.splitlines()

for region in result.regions:
    print("\n")
    print(f"Type:       {region.region_type}")
    print(f"Number:     {region.number}")
    print(f"Title:      {region.title}")
    print(f"Start line: {region.start_line}")

    start_line = region.start_line

    start_index = max(0, start_line - 3)
    end_index = min(len(lines), start_line + 2)

    print("\nContext:")

    for index in range(start_index, end_index):
        print(f"[L{index + 1:05d}] {lines[index]}")