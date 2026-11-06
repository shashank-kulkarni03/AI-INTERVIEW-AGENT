from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    Boolean,
    DateTime
)

from sqlalchemy.sql import func

from app.db.database import Base


class InterviewAnswer(Base):

    __tablename__ = "interview_answers"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    interview_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    question_number = Column(
        Integer,
        nullable=False
    )

    skill = Column(
        String(255),
        nullable=False
    )

    difficulty = Column(
        String(50),
        nullable=False
    )

    question_type = Column(
        String(50),
        default="technical"
    )

    question = Column(
        Text,
        nullable=False
    )

    answer = Column(
        Text,
        nullable=False
    )

    correctness = Column(
        Float,
        nullable=True
    )

    technical_depth = Column(
        Float,
        nullable=True
    )

    problem_solving = Column(
        Float,
        nullable=True
    )

    communication = Column(
        Float,
        nullable=True
    )

    overall_score = Column(
        Float,
        nullable=True
    )

    strengths = Column(
        Text,
        nullable=True
    )

    gaps = Column(
        Text,
        nullable=True
    )

    feedback = Column(
        Text,
        nullable=True
    )

    follow_up_required = Column(
        Boolean,
        default=False
    )

    follow_up_reason = Column(
        Text,
        nullable=True
    )

    is_follow_up = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )