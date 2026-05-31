from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.file_service import (
    save_uploaded_file,
    save_file_metadata
)
router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    saved_path = await save_uploaded_file(file)
    file_record = save_file_metadata(
    db=db,
    filename=file.filename,
    source_type=file.content_type
)
    return{
    "id": file_record.id,
    "message": "File uploaded successfully",
    "path": saved_path,
    "filename": file.filename,
    "content_type": file.content_type
}