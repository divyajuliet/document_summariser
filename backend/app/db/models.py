from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from backend.app.db.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    original_filename = Column(
        String,
        nullable=False
    )

    stored_filename = Column(
        String,
        nullable=False
    )

    file_type = Column(
        String,
        nullable=False
    )

    mime_type = Column(
        String,
        nullable=True
    )

    file_size = Column(
        Integer,
        nullable=False
    )

    status = Column(
        String,
        nullable=False,
        default="UPLOADED"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )