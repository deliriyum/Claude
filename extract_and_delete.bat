@echo off
setlocal enabledelayedexpansion

:: Check if any arguments were passed
if "%~1"=="" (
    echo No files selected!
    pause
    exit /b 1
)

:: Count total files
set total=0
for %%A in (%*) do set /a total+=1

:: If still 0, try alternate method
if %total%==0 (
    echo ERROR: No files received
    echo Arguments: %*
    pause
    exit /b 1
)

:: Set window title and size
title Extracting %total% archive(s)...
mode con: cols=80 lines=25

echo.
echo ========================================
echo  Extract and Delete - Processing %total% file(s)
echo ========================================
echo.

:: Process each archive
set current=0
set success=0
set failed=0

for %%A in (%*) do (
    set /a current+=1
    set "archive=%%~A"
    set "folder=%%~dpnA"

    echo [!current!/%total%] Extracting: %%~nxA

    "%ProgramFiles%\7-Zip\7z.exe" x "!archive!" -o"!folder!\" -y >nul 2>&1

    if !errorlevel!==0 (
        del "!archive!" >nul 2>&1
        if !errorlevel!==0 (
            echo           SUCCESS - Archive deleted
            set /a success+=1
        ) else (
            echo           WARNING - Extracted but could not delete
            set /a success+=1
        )
    ) else (
        echo           FAILED - Archive NOT deleted
        set /a failed+=1
    )
    echo.
)

:: Summary
echo ========================================
echo  Complete!
echo ========================================
echo  Total:   %total%
echo  Success: %success%
echo  Failed:  %failed%
echo ========================================
echo.

:: Keep window open for 3 seconds to see results
echo Closing in 3 seconds...
timeout /t 3 >nul

endlocal
