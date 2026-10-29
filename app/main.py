
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base, get_db
from app.seed_data import init_db_data

from app.routes import (
    auth,
    jobs,
    candidates,
    interviews,
    evaluations,
    statistics,
    ai,
    settings as sys_settings,
)

# =====================================================
# 1. CAU HINH THU MUC
# =====================================================

CURRENT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = CURRENT_DIR / "templates"
STATIC_DIR = CURRENT_DIR / "static"

STATIC_DIR.mkdir(parents=True, exist_ok=True)

UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

templates = Jinja2Templates(
    directory=str(TEMPLATES_DIR)
)

# =====================================================
# 2. KHOI TAO DATABASE
# =====================================================

Base.metadata.create_all(bind=engine)


# =====================================================
# 3. STARTUP & SHUTDOWN
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khoi tao du lieu mau khi server bat dau
    db_generator = get_db()
    db = next(db_generator)

    try:
        init_db_data(db)
    finally:
        db_generator.close()

    yield


# =====================================================
# 4. KHOI TAO FASTAPI
# =====================================================

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Hệ thống Quản lý Tuyển dụng Tích hợp AI "
        "- AIA331 - Đại học Thái Nguyên ICTU"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# =====================================================
# 5. CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# 6. STATIC FILES
# =====================================================

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)

app.mount(
    "/uploads",
    StaticFiles(directory=str(UPLOAD_DIR)),
    name="uploads",
)

# =====================================================
# 7. SUA LOI FAVICON 404
# =====================================================

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    favicon_path = STATIC_DIR / "favicon.ico"

    if favicon_path.is_file():
        return FileResponse(
            path=str(favicon_path),
            media_type="image/x-icon",
        )

    # Chua co favicon thi khong bao loi 404
    return Response(status_code=204)


# =====================================================
# 8. DANG KY ROUTERS
# =====================================================

app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(candidates.router)
app.include_router(interviews.router)
app.include_router(evaluations.router)
app.include_router(statistics.router)
app.include_router(ai.router)
app.include_router(sys_settings.router)

# =====================================================
# 9. TRANG CHU
# =====================================================

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.APP_NAME
        },
    )


# =====================================================
# 10. HEALTH CHECK
# =====================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "academic_course": (
            "AIA331 - Ứng dụng Trí tuệ Nhân tạo"
        ),
        "university": (
            "Đại học Thái Nguyên - "
            "Trường ĐH CNTT & TT (ICTU)"
        ),
    }
