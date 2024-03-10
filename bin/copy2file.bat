@echo off
echo.
echo copy file to it should exist directly.
echo.

set jarDir=C:\Users\Administrator\Desktop\huaxi03\WestChina-Cloud\
set targetDir=C:\Users\Administrator\Desktop\huaxi03\WestChina-Cloud\runall\
rem   Required startup items
xcopy %jarDir%westChina-gateway\target\westChina-gateway.jar %targetDir% /y
xcopy %jarDir%westChina-auth\target\westChina-auth.jar %targetDir% /y
xcopy %jarDir%westChina-modules\westChina-system\target\westChina-modules-system.jar %targetDir% /y

@REM A service that tenants
xcopy %jarDir%westChina-modules\westChina-tenant\target\westChina-modules-tenant.jar %targetDir% /y
@REM A service that generates code
xcopy %jarDir%westChina-modules\westChina-gen\target\westChina-modules-gen.jar %targetDir% /y
@REM @REM A service that Log
xcopy %jarDir%westChina-modules\westChina-job\target\westChina-modules-job.jar %targetDir% /y
@REM  A service that uploads file.
xcopy %jarDir%westChina-modules\westChina-file\target\westChina-modules-file.jar %targetDir% /y

@REM A service that monitor system.
xcopy %jarDir%westChina-visual\westChina-monitor\target\westChina-visual-monitor.jar %targetDir% /y

@REM A service that build of yourself.
xcopy %jarDir%westChina-modules\westChina-ct\target\westChina-modules-ct.jar %targetDir% /y




@REM Front Server --UI
@REM set uiDir=D:\000-inbox\Desktop\WestChina-Cloud\westChina-ui\
@REM set uiTargetDir=D:\000-inbox\Desktop\WestChina-Cloud\docker\nginx\html\
@REM
@REM xcopy %uiDir%administrator\dist\* %uiTargetDir%administrator\ /y /e
@REM xcopy %uiDir%ct\dist\* %uiTargetDir%ct\ /y /e
@REM xcopy %uiDir%main\dist\* %uiTargetDir%main\ /y /e

pause