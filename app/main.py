from fastapi import FastAPI
from app.database import Base, engine
from app import models
from app.routers.auth import router as auth_router

app = FastAPI(title="Electronic Dean's Office")

app.include_router(auth_router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Electronic Dean's Office API"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "SQLite",
        "tables": len(Base.metadata.tables),
    }
