from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict
import httpx

from app.database import get_db
from app.models import SystemSetting
from app.config import settings

router = APIRouter(prefix="/api/settings", tags=["Cài đặt Hệ thống & AI Engine"])

class SettingsUpdate(BaseModel):
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    ai_provider: Optional[str] = "auto"

@router.get("")
def get_settings(db: Session = Depends(get_db)):
    gemini_setting = db.query(SystemSetting).filter(SystemSetting.key_name == "GEMINI_API_KEY").first()
    openai_setting = db.query(SystemSetting).filter(SystemSetting.key_name == "OPENAI_API_KEY").first()
    provider_setting = db.query(SystemSetting).filter(SystemSetting.key_name == "AI_PROVIDER").first()

    gemini_val = (gemini_setting.key_value if gemini_setting else "") or settings.GEMINI_API_KEY
    openai_val = (openai_setting.key_value if openai_setting else "") or settings.OPENAI_API_KEY
    masked_gemini = (gemini_val[:6] + "..." + gemini_val[-4:]) if len(gemini_val) > 10 else ("Đã cấu hình" if gemini_val else "Chưa cấu hình (Đang dùng Heuristic Fallback)")
    masked_openai = (openai_val[:6] + "..." + openai_val[-4:]) if len(openai_val) > 10 else ("Đã cấu hình" if openai_val else "Chưa cấu hình")

    return {
        "app_name": settings.APP_NAME,
        "ai_provider": (provider_setting.key_value if provider_setting else settings.AI_PROVIDER),
        "gemini_api_key_status": masked_gemini,
        "openai_api_key_status": masked_openai,
        "has_gemini_key": bool(gemini_val),
        "has_openai_key": bool(openai_val),
        "active_engine": "Google Gemini 2.5/1.5 Flash" if gemini_val else ("OpenAI GPT-4o Mini" if openai_val else "Heuristic / Rule-based NLP Engine (Offline & An toàn Đạo đức)")
    }

@router.post("")
def save_settings(update_data: SettingsUpdate, db: Session = Depends(get_db)):
    if update_data.gemini_api_key is not None:
        setting = db.query(SystemSetting).filter(SystemSetting.key_name == "GEMINI_API_KEY").first()
        if not setting:
            setting = SystemSetting(key_name="GEMINI_API_KEY", key_value=update_data.gemini_api_key.strip(), description="Google Gemini API Key")
            db.add(setting)
        else:
            setting.key_value = update_data.gemini_api_key.strip()

    if update_data.openai_api_key is not None:
        setting = db.query(SystemSetting).filter(SystemSetting.key_name == "OPENAI_API_KEY").first()
        if not setting:
            setting = SystemSetting(key_name="OPENAI_API_KEY", key_value=update_data.openai_api_key.strip(), description="OpenAI API Key")
            db.add(setting)
        else:
            setting.key_value = update_data.openai_api_key.strip()

    if update_data.ai_provider:
        p_setting = db.query(SystemSetting).filter(SystemSetting.key_name == "AI_PROVIDER").first()
        if not p_setting:
            p_setting = SystemSetting(key_name="AI_PROVIDER", key_value=update_data.ai_provider, description="AI Provider")
            db.add(p_setting)
        else:
            p_setting.key_value = update_data.ai_provider

    db.commit()
    return {"message": "Đã lưu cài đặt AI Engine thành công!"}

@router.post("/test-gemini-key")
async def test_gemini_key(payload: Dict[str, str]):
    key = payload.get("api_key", "").strip()
    if not key:
        raise HTTPException(status_code=400, detail="Vui lòng nhập API Key cần kiểm tra")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json={"contents": [{"parts": [{"text": "Xin chào, phản hồi 1 từ 'OK'."}]}]})
            if resp.status_code == 200:
                return {"valid": True, "message": "Kết nối thành công với Google Gemini API!"}
            else:
                return {"valid": False, "message": f"API trả về mã lỗi: {resp.status_code} ({resp.text[:100]})"}
    except Exception as e:
        return {"valid": False, "message": f"Lỗi kết nối mạng: {str(e)}"}
