@ECHO OFF
SETLOCAL enabledelayedexpansion


@REM :: insert your files here
SET "MAP_FILE=..\path\to\mdd_map_R2401582.xlsx"

SET "MDD_FILE=..\path\to\R2401582.mdd"











@REM :: do you need an html file with fields from MDD? It is quite useful
@REM :: set to "1==1" (which means true in bat files) to have this file generated
SET "CONFIG_PRODUCE_HTML_MDD=1==1"

@REM :: set to "1==1" if you don't need unnecessary files generated by the script - steps taken when produucing final files
@REM :: or, set to "1==0" to have these files stored for debugging
SET "CLEAN_TEMP_MIDDLE_FILES=1==1"


SET "MDD_FILE_SCHEME=%MDD_FILE%.json"
SET "RESULT_FILE=%MAP_FILE%_filled_with_script.xlsx"

ECHO -
ECHO 1. read MDD
ECHO read from: %MDD_FILE%
ECHO write to: .json
python dist/mdmtoolsap_prefill_flatout_bundle.py --program read_mdd --mdd "%MDD_FILE%" --config-features label,attributes,properties,scripting --config-section fields --config-contexts Analysis,Question
if %ERRORLEVEL% NEQ 0 ( echo ERROR: Failure && pause && goto CLEANUP && exit /b %errorlevel% )

IF %CONFIG_PRODUCE_HTML_MDD% (
    ECHO -
    ECHO 1.1. generate html
    python dist/mdmtoolsap_prefill_flatout_bundle.py --program report --inpfile "%MDD_FILE_SCHEME%"
    if %ERRORLEVEL% NEQ 0 ( echo ERROR: Failure && pause && goto CLEANUP && exit /b %errorlevel% )
)

ECHO -
ECHO 2. produce filled map
python dist/mdmtoolsap_prefill_flatout_bundle.py --program fill-map --inp-mdd-scheme "%MDD_FILE_SCHEME%" --map "%MAP_FILE%" --output-filename "%RESULT_FILE%"
if %ERRORLEVEL% NEQ 0 ( echo ERROR: Failure && pause && goto CLEANUP && exit /b %errorlevel% )




ECHO -
ECHO 7 del .json temporary files

IF %CLEAN_TEMP_MIDDLE_FILES% (
    DEL "%MDD_FILE_SCHEME%"
)

ECHO -
:CLEANUP
ECHO 999. Clean up
REM REM :: comment: just deleting trach .pyc files after the execution - they are saved when modules are loaded from within bndle file created with pinliner
REM REM :: however, it is necessary to delete these .pyc files before every call of the mdmtoolsap_prefill_flatout_bundle
REM REM :: it means, 6 more times here, in this script; but I don't do it cause I have this added to the linliner code - see my pinliner fork
DEL *.pyc
IF EXIST __pycache__ (
DEL /F /Q __pycache__\*
)
IF EXIST __pycache__ (
RMDIR /Q /S __pycache__
)

ECHO done!
exit /b %errorlevel%

