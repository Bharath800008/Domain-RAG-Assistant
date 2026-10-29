"""FastAPI app entrypoint: CORS, router includes, table creation."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from database import Base, engine
from routers import (
    auth_routes,
    documents_routes,
    chat_routes,
    feedback_routes,
    analytics_routes,
    settings_routes,
    explorer_routes,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Domain RAG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": f"Internal server error: {str(exc)}"})


app.include_router(auth_routes.router)
app.include_router(documents_routes.router)
app.include_router(chat_routes.router)
app.include_router(feedback_routes.router)
app.include_router(analytics_routes.router)
app.include_router(settings_routes.router)
app.include_router(explorer_routes.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
