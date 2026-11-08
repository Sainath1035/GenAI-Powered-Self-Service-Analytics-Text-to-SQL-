@echo off
set GIT_PATH=C:\Users\outsm\.gemini\antigravity\bin\git\cmd\git.exe
echo ========================================================
echo        Push Text-to-SQL Chatbot to GitHub
echo ========================================================
echo.
set /p REPO_URL="Enter your GitHub Repository URL (e.g. https://github.com/username/Text-to-SQL-Chatbot.git): "

if "%REPO_URL%"=="" (
    echo [ERROR] Repository URL cannot be empty.
    pause
    exit /b 1
)

echo.
echo Adding remote origin...
"%GIT_PATH%" remote remove origin 2>nul
"%GIT_PATH%" remote add origin %REPO_URL%
"%GIT_PATH%" branch -M main

echo Pushing code to %REPO_URL%...
"%GIT_PATH%" push -u origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo [SUCCESS] Your repository has been uploaded to GitHub!
) else (
    echo.
    echo [NOTE] If authentication is required, make sure you are logged in or use a GitHub Personal Access Token.
)

pause
