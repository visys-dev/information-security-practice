from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from app.audit.middleware import AuditMiddleware
from app.audit.router import router as audit_router
from app.database import Base, engine
from app.middleware.csrf import CSRFMiddleware
from app.middleware.rate_limiter import limiter
from app.middleware.security_headers import SecurityHeadersMiddleware
from app import models
from app.audit import models as audit_models
from app.routers.auth import router as auth_router
from app.routers.admin import router as admin_router
from app.routers.demo import router as demo_router
from app.routers.students import router as students_router
from app.routers.teachers import router as teachers_router

app = FastAPI(title="Electronic Dean's Office")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3010",
    "http://localhost:8000",
]

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFMiddleware, allowed_origins=allowed_origins)
app.add_middleware(AuditMiddleware)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router)
app.include_router(students_router)
app.include_router(teachers_router)
app.include_router(admin_router)
app.include_router(audit_router, prefix="/admin", tags=["Audit"])
app.include_router(demo_router)


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
