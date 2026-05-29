from sqlalchemy import Column, Integer, String
from app.db.database import Base

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    source_type = Column(String, nullable=False)