import logging
import tempfile
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.core.config import Settings, get_settings
from app.core.exceptions import InvalidDocumentError, ThesisFormatError, UnsupportedDegreeError
from app.core.logging import configure_logging
from app.llm.provider import build_llm_provider
from app.rules.loader import list_supported_degrees
from app.services.factory import build_docx_engine, build_structure_recognizer
from app.services.processor import ThesisProcessor

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="Thesis Format Fixer Demo", version="0.1.0", lifespan=lifespan)


def get_processor(settings: Settings = Depends(get_settings)) -> ThesisProcessor:
    provider = build_llm_provider(
        settings.llm_provider,
        settings.llm_api_key,
        settings.llm_endpoint,
        settings.llm_model,
        settings.llm_timeout_seconds,
        settings.llm_audit_log_path,
    )
    recognizer = build_structure_recognizer(settings.structure_recognizer, provider)
    return ThesisProcessor(
        build_docx_engine(settings.docx_engine),
        provider,
        settings.storage_dir,
        recognizer=recognizer,
    )


settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "supported_degrees": list_supported_degrees()}


@app.post("/api/process")
async def process_docx(
    file: UploadFile = File(...),
    degree: str = Form("undergraduate"),
    processor: ThesisProcessor = Depends(get_processor),
    runtime_settings: Settings = Depends(get_settings),
) -> FileResponse:
    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx uploads are supported.")

    content = await file.read()
    max_bytes = runtime_settings.max_upload_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413, detail=f"File exceeds {runtime_settings.max_upload_mb} MB."
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        upload_path = Path(temp_dir) / "upload.docx"
        upload_path.write_bytes(content)
        try:
            result = processor.process(upload_path, degree)
        except UnsupportedDegreeError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except InvalidDocumentError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except ThesisFormatError as exc:
            logger.exception("Application processing error")
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except Exception as exc:
            logger.exception("Unexpected processing error")
            raise HTTPException(status_code=500, detail="Document processing failed.") from exc

    return FileResponse(
        result.archive_path,
        media_type="application/zip",
        filename="thesis_format_fix_result.zip",
    )
