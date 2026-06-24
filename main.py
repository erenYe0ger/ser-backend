from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.routers.auth import router as auth_router
from app.core.config import settings
from app.core.database import Base, engine

# Create the FastAPI application instance
app = FastAPI(title=settings.APP_NAME)

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