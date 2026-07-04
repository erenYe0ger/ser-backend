from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware

from app.api.routes import router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.limiter import limiter
from app.routers.auth import router as auth_router

# Create the FastAPI application instance
app = FastAPI(title=settings.APP_NAME)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

# SlowAPI middleware should be added before other middleware
app.add_middleware(SlowAPIMiddleware)

# Allow React frontend to call the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://ser-frontend-eight.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create all database tables when the application starts
@app.on_event("startup")
async def startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Register API routes under the versioned API prefix
app.include_router(router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")


# Health check / root endpoint
@app.get("/")
async def root():
    return {
        "message": "SER Backend is running",
        "docs": "/docs",
    }