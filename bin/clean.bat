@echo off
echo.
echo clean all target
echo.

%~d0
cd %~dp0

cd ..
call mvn clean

cd bin
pause