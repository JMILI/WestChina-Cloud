@echo off
echo.
echo [��Ϣ] monitor��
echo.

cd %~dp0
cd ../westChina-visual/westChina-monitor/target

set JAVA_OPTS=-Xms512m -Xmx1024m -XX:MetaspaceSize=128m -XX:MaxMetaspaceSize=512m

java -Dfile.encoding=utf-8 %JAVA_OPTS% -jar westChina-visual-monitor.jar