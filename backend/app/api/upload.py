from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.services.file_service import (
    save_uploaded_file,
    save_file_metadata
)

from app.services.parser_service import parse_txt
from app.services.chunk_service import create_chunks
from app.services.vector_store import add_chunks

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Save file
    saved_path = await save_uploaded_file(file)

    # Save metadata
    file_record = save_file_metadata(
        db=db,
        filename=file.filename,
        source_type=file.content_type
    )

    # Parse file
    text = parse_txt(saved_path)

    # Create chunks
    chunks = create_chunks(text)

    # Store chunks in ChromaDB
    add_chunks(chunks)

    return {
        "id": file_record.id,
        "message": "File uploaded successfully",
        "path": saved_path,
        "filename": file.filename,
        "content_type": file.content_type,
        "chunks_created": len(chunks)
    }