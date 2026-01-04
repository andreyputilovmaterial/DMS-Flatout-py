@ECHO OFF

ECHO Clear up dist\...
IF EXIST dist (
    REM -
) ELSE (
    MKDIR dist
)
DEL /F /Q dist\*

ECHO Calling pinliner...
REM REM :: comment: please delete .pyc files before every call of the mdmtoolsap_prefill_flatout_bundle - this is implemented in my fork of the pinliner
@REM python src-make\lib\pinliner\pinliner\pinliner.py src -o dist/mdmtoolsap_prefill_flatout_bundle.py --verbose
python src-make\lib\pinliner\pinliner\pinliner.py src -o dist/mdmtoolsap_prefill_flatout_bundle.py
if %ERRORLEVEL% NEQ 0 ( echo ERROR: Failure && pause && exit /b %errorlevel% )
ECHO Done

ECHO Patching mdmtoolsap_prefill_flatout_bundle.py...
ECHO # ... >> dist/mdmtoolsap_prefill_flatout_bundle.py
ECHO # print('within mdmtoolsap_prefill_flatout_bundle') >> dist/mdmtoolsap_prefill_flatout_bundle.py
REM REM :: no need for this, the root package is loaded automatically
@REM ECHO # import mdmtoolsap_prefill_flatout_bundle >> dist/mdmtoolsap_prefill_flatout_bundle.py
ECHO from src import launcher >> dist/mdmtoolsap_prefill_flatout_bundle.py
ECHO launcher.main() >> dist/mdmtoolsap_prefill_flatout_bundle.py
ECHO # print('out of mdmtoolsap_prefill_flatout_bundle') >> dist/mdmtoolsap_prefill_flatout_bundle.py

PUSHD dist
COPY ..\run.bat .\run_fill_flatout_map.bat
powershell -Command "(gc 'run_fill_flatout_map.bat' -encoding 'Default') -replace '(dist[/\\])?mdmtoolsap_prefill_flatout_bundle.py', 'mdmtoolsap_prefill_flatout_bundle.py' | Out-File -encoding 'Default' 'run_fill_flatout_map.bat'"
POPD


ECHO End

