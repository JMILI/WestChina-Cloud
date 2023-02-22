@echo off
echo.
echo [��Ϣ] job��
echo.


cd %~dp0
cd ../westChina-modules/westChina-job/target

set JAVA_OPTS=-Xms512m -Xmx1024m -XX:MetaspaceSize=128m -XX:MaxMetaspaceSize=512m

java -Dfile.encoding=utf-8 %JAVA_OPTS% -jar westChina-modules-job.jar