@echo off
echo.
echo [run all ] jar scripts
echo.

cd %~dp0
cd ../runall
@REM start taskkill /f /im java.exe
@REM start redis
@REM ping westChinaBackend -n 1
@REM start nacos
@REM
@REM ping westChinaBackend -n 30
@REM
set JAVA_OPTS=-Xms512m -Xmx1024m -XX:MetaspaceSize=128m -XX:MaxMetaspaceSize=512m

@REM @REM
start cmd /c "title auth && java -jar -Dfile.encoding=utf-8 %JAVA_OPTS% -jar westChina-auth.jar &"
ping westChinaBackend -n 2
start cmd /c "title gateway && java -jar -Dfile.encoding=utf-8 %JAVA_OPTS% -jar westChina-gateway.jar &"
ping westChinaBackend -n 2
start cmd /c  "title system && java -jar -Dfile.encoding=utf-8 %JAVA_OPTS% -jar westChina-modules-system.jar &"

ping westChinaBackend -n 20
@REM
start cmd /c "title ct && java -jar -Dfile.encoding=utf-8 %JAVA_OPTS% -jar westChina-modules-ct.jar &"
ping westChinaBackend -n 2

start cmd /c "title file && java -jar -Dfile.encoding=utf-8 %JAVA_OPTS% -jar westChina-modules-file.jar &"
ping westChinaBackend -n 2
start cmd /c "title tenant && java -jar -Dfile.encoding=utf-8 %JAVA_OPTS% -jar westChina-modules-tenant.jar &"
ping westChinaBackend -n 2
@REM
@REM @REM
start cmd /c "title gen && java -jar -Dfile.encoding=utf-8 %JAVA_OPTS% -jar westChina-modules-gen.jar &"
ping westChinaBackend -n 2
start cmd /c  "title job && java -jar -Dfile.encoding=utf-8 %JAVA_OPTS% -jar westChina-modules-job.jar &"
ping westChinaBackend -n 2
start cmd /c "title monitor && java -jar -Dfile.encoding=utf-8 %JAVA_OPTS% -jar westChina-visual-monitor.jar &"
ping westChinaBackend -n 2

cd ../bin
pause
