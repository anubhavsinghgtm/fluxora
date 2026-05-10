import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.v1.routes import router
from app.core.config import get_settings
from app.core.exceptions import (
    AppException,
    DatabaseQueryException,
    InvalidSQLGeneratedException,
    LLMQuotaExceededException,
    LLMException,
    SchemaFetchException,
)

settings = get_settings()

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — environment: %s", settings.APP_ENV)
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="Fluxora - Turn questions into data insights",
    description="Ask questions in plain English, get data back.",
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(router, prefix="/api/v1")


@app.exception_handler(InvalidSQLGeneratedException)
async def invalid_sql_handler(request: Request, exc: InvalidSQLGeneratedException):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(LLMQuotaExceededException)
async def quota_handler(request: Request, exc: LLMQuotaExceededException):
    return JSONResponse(status_code=429, content={"detail": str(exc)})


@app.exception_handler(LLMException)
async def llm_handler(request: Request, exc: LLMException):
    return JSONResponse(status_code=502, content={"detail": str(exc)})


@app.exception_handler(DatabaseQueryException)
async def db_query_handler(request: Request, exc: DatabaseQueryException):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(SchemaFetchException)
async def schema_handler(request: Request, exc: SchemaFetchException):
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(AppException)
async def generic_app_handler(request: Request, exc: AppException):
    logger.error("Unhandled app exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "env": settings.APP_ENV}