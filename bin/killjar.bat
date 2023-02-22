@echo off
echo.
echo [kill all jar task]。
echo.
@REM 关闭javaw进程，等同于关闭所有jar服务
start taskkill /f /im javaw.exe
start taskkill /f /im java.exe