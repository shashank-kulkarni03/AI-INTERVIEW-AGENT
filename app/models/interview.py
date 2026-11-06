from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime
)

from sqlalchemy.sql import func

from app.db.database import Base


class Interview(Base):

    __tablename__ = "interviews"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    candidate_id = Column(
        Integer,
        nullable=False
    )

    job_id = Column(
        Integer,
        nullable=False
    )

    role = Column(
        String(255),
        nullable=False
    )

    status = Column(
        String(50),
        default="active"
    )

    alignment_score = Column(
        Float,
        nullable=True
    )

    question_count = Column(
        Integer,
        default=0
    )

    final_score = Column(
        Float,
        nullable=True
    )

    recommendation = Column(
        String(100),
        nullable=True
    )

    final_report = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )