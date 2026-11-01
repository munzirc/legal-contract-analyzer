
from typing import TypedDict


class FunctionParameters(TypedDict):
    type: str
    properties: dict[str, object]
    required: list[str]


class ToolDeclaration(TypedDict):
    type: str
    name: str
    description: str
    parameters: FunctionParameters



set_document_serach_declaration: ToolDeclaration = {
    "type": "function",
    "name": "document_search",
    "description": (
        "Search user-selected legal documents for passages relevant to "
        "the user's question using semantic similarity. Use this tool "
        "to find evidence about contractual obligations, terms, conditions, "
        "amounts, deadlines, rights, and other topics. "
        "For questions comparing multiple documents, include all relevant "
        "selected document IDs in a single call. "
        "This tool can run independently and in parallel with "
        "get_document_structure when both semantic search and structural "
        "inspection are useful. Use the returned passages and their "
        "source metadata to determine whether further retrieval is needed."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The question or topic to search for.",
            },
            "document_ids": {
                "type": "array",
                "items": {
                    "type": "string",
                },
                "description": (
                    "IDs of the user-selected documents to search."
                ),
            },
        },
        "required": ["query", "document_ids"],
    },
}

get_document_structure_declaration : ToolDeclaration = {
    "type": "function",
    "name": "get_document_structure",
    "description": (
        "Retrieve the structural hierarchy of the user-selected documents, "
        "including section identifiers, section titles, subsection "
        "identifiers, and subsection titles. Use this tool when you need "
        "to discover where relevant contractual provisions may be located "
        "or when investigating a document's organization. "
        "This tool can run independently and in parallel with "
        "document_search. Use its results to identify the exact section "
        "or subsection identifiers and titles needed for subsequent "
        "get_sections calls. Do not call it unnecessarily when the "
        "available evidence is already sufficient."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}


get_section_declaration: ToolDeclaration = {
    "type": "function",
    "name": "get_sections",
    "description": (
        "Retrieve the text of specific sections or subsections from one "
        "user-selected legal document. Provide section identifiers, "
        "section titles, subsection identifiers, or subsection titles "
        "as section_queries. When the relevant identifiers or titles are "
        "unknown, first call get_document_structure and use its results "
        "to construct these queries. If the identifiers or titles are "
        "already known, this tool can be called directly. "
        "Each call accepts up to five unique section queries for one "
        "document. Use this tool to inspect complete relevant provisions "
        "when semantic search results alone do not provide sufficient "
        "context. Do not invent section identifiers or titles."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "document_id": {
                "type": "string",
                "description": (
                    "UUID of a document selected by the user."
                ),
            },
            "section_queries": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "Up to five section or subsection identifiers "
                    "or title phrases to search for."
                ),
            },
        },
        "required": ["document_id", "section_queries"],
    },
}
