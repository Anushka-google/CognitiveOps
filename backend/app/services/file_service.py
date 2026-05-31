from pathlib import Path
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.upload_file import UploadedFile



UPLOAD_DIR = Path("uploads")


async def save_uploaded_file(file: UploadFile):
    file_path = UPLOAD_DIR / file.filename

    content = await file.read()

    with open(file_path, "wb") as buffer:
        buffer.write(content)

    return str(file_path)

def save_file_metadata(
    db: Session,
    filename: str,
    source_type: str
):
    file_record = UploadedFile(
        filename=filename,
        source_type=source_type
    )

    db.add(file_record)

    db.commit()

    db.refresh(file_record)

    return file_record