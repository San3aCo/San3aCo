@echo off
cd /d "%~dp0"
git add .
git commit -m "تحديث تلقائي %date% %time%"
git push
echo.
echo ✅ تم الرفع!
pause
