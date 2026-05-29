from app.db.database import engine, Base
from app.models.upload_file import UploadedFile

Base.metadata.create_all(bind=engine)

print("✅ Tables Created")