@echo off
cd /d "%~dp0"
echo ========================================
echo   一切皆蒸馏 - 知识蒸馏备考平台
echo ========================================
echo.
echo 正在启动应用...
echo 浏览器会自动打开 http://localhost:8501
echo 按 Ctrl+C 停止应用
echo.
streamlit run app.py --server.port 8501
pause
