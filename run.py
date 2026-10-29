import sys
import os

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import uvicorn

# Đảm bảo đường dẫn thư mục hiện tại nằm trong sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if __name__ == "__main__":
    print("=" * 70)
    print("  HỆ THỐNG QUẢN LÝ TUYỂN DỤNG CÓ TÍCH HỢP AI - AIA331")
    print("  ĐẠI HỌC THÁI NGUYÊN - TRƯỜNG ĐH CNTT VÀ TRUYỀN THÔNG (ICTU)")
    print("=" * 70)
    print("  Giao diện Web:   http://127.0.0.1:8000")
    print("  Tài liệu Swagger: http://127.0.0.1:8000/docs")
    print("  Kiểm tra API:    http://127.0.0.1:8000/health")
    print("=" * 70)
    print("  ⚠️  Lưu ý: AI chỉ hỗ trợ, quyết định tuyển dụng do con người.")
    print("=" * 70)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)