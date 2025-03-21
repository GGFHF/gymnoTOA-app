@echo off

rem ----------------------------------------------------------------------------

rem This script performs a test of the program calculate-enrichment-analysis.py
rem in a Windows environment.
rem
rem This software has been developed by:
rem
rem     GI en Desarrollo de Especies y Comunidades Leñosas (WooSp)
rem     Dpto. Sistemas y Recursos Naturales
rem     ETSI Montes, Forestal y del Medio Natural
rem     Universidad Politecnica de Madrid
rem     https://github.com/ggfhf/
rem
rem Licence: GNU General Public Licence Version 3.

rem ----------------------------------------------------------------------------

rem Control parameters

if not "%*" == "" (set ERROR=1 & goto END)

rem ----------------------------------------------------------------------------

rem Set environment

setlocal EnableDelayedExpansion

set ERROR=0

set PYTHON=python.exe
set PYTHON_OPTIONS=
set PYTHONPATH=.

set APP_DIR=C:\Users\FMM\Documents\ProyectosVS\gymnoTOA\gymnoTOA
set DATA_DIR=%APP_DIR%\data
set OUTPUT_DIR=%APP_DIR%\output

if not exist %OUTPUT_DIR% (mkdir %OUTPUT_DIR%)

set INITIAL_DIR=%cd%
cd %APP_DIR%

rem ----------------------------------------------------------------------------

rem Execute the program calculate-enrichment-analysis.py

%PYTHON% %PYTHON_OPTIONS% calculate-enrichment-analysis.py ^
    --db=%DATA_DIR%\gymnoTOA.db ^
    --annotations=%OUTPUT_DIR%\annotations.csv ^
    --species="Pinus taeda" ^
    --method=by ^
    --msqannot=5 ^
    --msqspec=10 ^
    --goea=%OUTPUT_DIR%\goterm-enrichment-analysis.csv ^
    --mpea=%OUTPUT_DIR%\metacyc-pathway-enrichment-analysis.csv ^
    --koea=%OUTPUT_DIR%\kegg-ko-enrichment-analysis.csv ^
    --kpea=%OUTPUT_DIR%\kegg-pathway-enrichment-analysis.csv ^
    --verbose=Y ^
    --trace=N
if %ERRORLEVEL% neq 0 (set RC=%ERRORLEVEL% & set ERROR=2 & goto END)

rem ----------------------------------------------------------------------------

:END

cd %INITIAL_DIR%

if %ERROR% equ 0 (
    rem -- exit 0
)

if %ERROR% equ 1 (
    echo *** ERROR: This script does not have input parameters.
    rem -- pause
    rem -- exit %RC%
)

if %ERROR% equ 2 (
    echo *** ERROR: The program ended with return code %RC%.
    rem -- pause
    rem -- exit %RC%
)

rem ----------------------------------------------------------------------------
