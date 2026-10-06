
import time
import uuid
from pathlib import Path

from app.db.database import SessionLocal
from app.models.document_model import Document

from app.services.document_service.extraction_service.extract_document import extract_document
from app.services.document_service.extraction_service.structure_analyzer import detect_structure
from app.services.document_service.chunking_service.region_builder import build_regions
from app.services.document_service.extraction_service.canonical_text_builder import CanonicalDocument, build_canonical_text
from app.services.document_service.extraction_service.extract_document import ExtractedDocument
from app.services.document_service.chunking_service.region_builder import DocumentRegion

from test_script import test_sentence_splitter


output_path = Path("regions_output.txt")

def process_document(document_id: uuid.UUID) -> None:
    
    db = SessionLocal()
    
    try:
        # Fetch the document from the database using the provided document_id
        document: Document | None = db.get(Document, document_id)
        
        if document is None:
            print(f"Document with ID {document_id} not found.")
            return
        
        print(f"Processing document: {document.filename}")
        
        # Read the PDF file content
        with open(document.pdf_storage_path, "rb") as file:
            file_content = file.read()

        # Extract the document content and metadata
        extracted_document : ExtractedDocument = extract_document(
            file_content=file_content,
        )
        
        # Build the canonical text from the extracted document
        canonical_document: CanonicalDocument = build_canonical_text(extracted_document)
        
        # save the canonical text to the database
        document.canonical_text = canonical_document.text
        db.commit()
        
        # Detect the structure of the canonical text   
        document_structure = detect_structure(canonical_document.text)

        # Build regions based on the canonical text and detected structure
        regions = build_regions(              
            text=canonical_document.text,
            structure=document_structure
        )   
        
        
        chunks = test_sentence_splitter(
            text=canonical_document.text,
            regions=regions,
        )
        
        
        with open("chunks_output.txt", "w", encoding="utf-8") as file:

            for chunk in chunks:

                file.write(
                    f"\nCHUNK {chunk.chunk_index}"
                    f"\nOffset: {chunk.start_offset} -> {chunk.end_offset}"
                    f"\nSection: {chunk.section_number} {chunk.section_title}"
                    f"\nLength: {len(chunk.text)}"
                    f"\n{chunk.text}"
                    f"\n{'-' * 80}\n"
                )
        
        
        
        
        # write_regions(regions, canonical_document.text)
        
        
        
        
        
        
        
    except Exception as e:
        print(f"Error processing document {document_id}: {e}")
    
    finally:
        db.close()
        
        
        


def write_regions(regions : list[DocumentRegion], canonical_text: str) -> None:
    with output_path.open("w", encoding="utf-8") as file:
        for index, region in enumerate(regions, start=1):
            region_text = canonical_text[
                region.start_offset:region.end_offset
            ]
            
            file.write(time.strftime("%Y-%m-%d %H:%M:%S") + "\n")

            file.write("=" * 80 + "\n")
            file.write(f"REGION {index}\n")
            file.write("=" * 80 + "\n")

            file.write(f"Type: {region.region_type}\n")
            file.write(f"Identifier: {region.identifier}\n")
            file.write(f"Title: {region.title}\n")
            file.write(f"Start line: {region.start_line}\n")
            file.write(f"End line: {region.end_line}\n")
            file.write(f"Start offset: {region.start_offset}\n")
            file.write(f"End offset: {region.end_offset}\n")

            file.write("\n")
            file.write(region_text)
            file.write("\n\n")
            
    print(f"Regions written to {output_path.resolve()}")