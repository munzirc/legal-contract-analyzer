def analyzer_prompt(numbered_text: str) -> str:
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
    5. For structures that have a number, letter, Roman numeral, exhibit identifier, or other designator, return it exactly as written in the document as "identifier".
    6. If a top-level region has a title, return its title.
    7. If a top-level region does not have an identifier, set "identifier" to null.
    8. If a top-level region does not have a clear title, set "title" to null.
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

    then identify only the following region:

    Type: SECTION
    Identifier: 1
    Title: PERFORMANCE OF SERVICES

    Do not identify 1.1, 1.2, or 1.3 as separate regions.

    The goal is to reconstruct the document's major structural hierarchy, not to identify every heading.

    The document below has been numbered line-by-line. Use those line numbers when identifying the start of each top-level region.

    The start_line must point to the line containing the region's own heading.

    Here is the document:

    {numbered_text}

    """    
    return prompt