from app.db.database import Base, engine

# Import every model so SQLAlchemy knows about them.
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.interview import Interview
from app.models.answer import InterviewAnswer


def init_db():
    Base.metadata.create_all(
        bind=engine
    )


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")