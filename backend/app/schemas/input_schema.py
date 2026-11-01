from uuid import UUID
from pydantic import BaseModel

class SelectedDocument(BaseModel):
    document_id: UUID
    filename: str
    
class Input(BaseModel):
    question : str
    selected_documents: list[SelectedDocument]
