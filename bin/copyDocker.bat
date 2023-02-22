@echo off
echo.
echo copy file to it should exist directly.
echo.
rem ����ļ��ƶ�
set jarDir=D:\000-inbox\Desktop\WestChina-Cloud\
set targetDir=D:\000-inbox\Desktop\WestChina-Cloud\docker\westChina\

xcopy %jarDir%westChina-gateway\target\westChina-gateway.jar %targetDir%gateway\jar\ /y
xcopy %jarDir%westChina-auth\target\westChina-auth.jar %targetDir%auth\jar\ /y
rem ·����һ��
xcopy %jarDir%westChina-visual\westChina-monitor\target\westChina-visual-monitor.jar %targetDir%visual\monitor\jar\ /y
rem ·����һ��
xcopy %jarDir%westChina-modules\westChina-file\target\westChina-modules-file.jar %targetDir%modules\file\jar\ /y
xcopy %jarDir%westChina-modules\westChina-gen\target\westChina-modules-gen.jar %targetDir%modules\gen\jar\ /y
xcopy %jarDir%westChina-modules\westChina-job\target\westChina-modules-job.jar %targetDir%modules\job\jar\ /y
xcopy %jarDir%westChina-modules\westChina-system\target\westChina-modules-system.jar %targetDir%modules\system\jar\ /y
xcopy %jarDir%westChina-modules\westChina-tenant\target\westChina-modules-tenant.jar %targetDir%modules\tenant\jar\ /y

xcopy %jarDir%westChina-modules\westChina-ct\target\westChina-modules-ct.jar %targetDir%modules\ct\jar\ /y


rem ǰ���ļ��ƶ�
@REM set uiDir=D:\000-inbox\Desktop\WestChina-Cloud\westChina-ui\
@REM set uiTargetDir=D:\000-inbox\Desktop\WestChina-Cloud\docker\nginx\html\
@REM
@REM xcopy %uiDir%administrator\dist\** %uiTargetDir%administrator\ /y /e
@REM xcopy %uiDir%ct\dist\** %uiTargetDir%ct\ /y /e
@REM xcopy %uiDir%main\dist\** %uiTargetDir%main\ /y /e


pause