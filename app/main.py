import os

from fastapi import FastAPI

from app.config import settings

from app.api import screening
from app.api import interviews
from app.api import reports

from app.db.init_db import init_db


app = FastAPI(
    title="AI Interview Agent",
    description=(
        "Agentic AI interview system using "
        "Gemini 2.5 Flash and MySQL."
    ),
    version="1.0.0"
)


@app.on_event("startup")
def startup():

    os.makedirs(
        settings.UPLOAD_DIR,
        exist_ok=True
    )

    init_db()


app.include_router(
    screening.router,
    prefix="/screening",
    tags=["Screening"]
)

app.include_router(
    interviews.router,
    prefix="/interviews",
    tags=["Interviews"]
)

app.include_router(
    reports.router,
    prefix="/reports",
    tags=["Reports"]
)


@app.get("/")
def root():

    return {
        "application":
            "AI Interview Agent",

        "status":
            "running",

        "model":
            "Gemini 2.5 Flash",

        "database":
            "MySQL"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }