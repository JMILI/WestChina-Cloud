@echo off
echo.
echo [JMILI prompt:]use maven build all modules!
echo.

%~d0
cd %~dp0

cd ..
call mvn clean package -Dmaven.test.skip=true

cd bin
pause