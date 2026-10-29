@echo off
chcp 65001 > nul
title Chạy Kiểm Thử Hệ Thống (Pytest Unit Tests)
echo ======================================================================
echo    ĐANG CHẠY BỘ KIỂM THỬ TỰ ĐỘNG PYTEST CHO DỰ ÁN AIA331
echo    Kiểm thử: Hồ sơ, Vòng phỏng vấn, Trạng thái, AI & Anti-Bias
echo ======================================================================
python -m pytest tests -v
echo ======================================================================
pause
