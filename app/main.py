from fastapi import FastAPI
from app.database import Base, engine
from app import models
from app.routers.auth import router as auth_router
from app.routers.admin import router as admin_router
from app.routers.students import router as students_router
from app.routers.teachers import router as teachers_router

app = FastAPI(title="Electronic Dean's Office")

app.include_router(auth_router)
app.include_router(students_router)
app.include_router(teachers_router)
app.include_router(admin_router)


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
