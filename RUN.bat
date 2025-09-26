@echo off
color 0B
title Bible MP3 Player

:MAIN
cls
echo ================================================
echo          Bible MP3 Player
echo ================================================
echo.
echo Select program to run:
echo.
echo   1. GUI Launcher (Recommended!)
echo   2. OneDrive Integrated App
echo   3. Basic Local App
echo   4. Main App
echo   5. System Check
echo   6. GitHub Upload Guide
echo   7. Help
echo   0. Exit
echo.
echo ================================================
set /p choice="Choice (0-7): "

if "%choice%"=="1" goto GUI_LAUNCHER
if "%choice%"=="2" goto ONEDRIVE_APP
if "%choice%"=="3" goto LOCAL_APP
if "%choice%"=="4" goto MAIN_APP
if "%choice%"=="5" goto SYSTEM_CHECK
if "%choice%"=="6" goto GITHUB_UPLOAD
if "%choice%"=="7" goto HELP
if "%choice%"=="0" goto EXIT
goto INVALID_CHOICE

:GUI_LAUNCHER
cls
echo Running GUI Launcher...
echo ========================
echo Starting Korean-supported GUI launcher
echo This is the most stable method!
echo.
python gui_launcher.py
if errorlevel 1 (
    echo.
    echo ERROR: GUI Launcher failed to run
    echo TIP: Install dependencies with: pip install kivy requests
    pause
)
goto MAIN

:ONEDRIVE_APP
cls
echo Running OneDrive Integrated App...
echo ==================================
echo Starting OneDrive cloud streaming app
echo Internet connection required
echo.
python kivy_onedrive_main.py
if errorlevel 1 (
    echo.
    echo ERROR: OneDrive app failed to run
    pause
)
goto MAIN

:LOCAL_APP
cls
echo Running Basic Local App...
echo ==========================
echo Starting local files only version
echo Works offline
echo.
python kivy_main.py
if errorlevel 1 (
    echo.
    echo ERROR: Local app failed to run
    pause
)
goto MAIN

:MAIN_APP
cls
echo Running Main App...
echo ===================
echo Starting main execution file
echo.
python main.py
if errorlevel 1 (
    echo.
    echo ERROR: Main app failed to run
    pause
)
goto MAIN

:SYSTEM_CHECK
cls
echo System Status Check...
echo ======================
echo.
echo Python Version:
python --version
echo.
echo Project Files:
dir /b *.py *.db *.spec *.txt
echo.
echo Python Packages Check:
echo Kivy Status:
python -c "import kivy; print('OK: Kivy', kivy.__version__)" 2>nul || echo "ERROR: Kivy not installed"
echo Requests Status:
python -c "import requests; print('OK: Requests', requests.__version__)" 2>nul || echo "ERROR: Requests not installed"
echo SQLite3 Status:
python -c "import sqlite3; print('OK: SQLite3 installed')" 2>nul || echo "ERROR: SQLite3 not installed"
echo.
echo Database File:
if exist "full_bible.db" (
    echo OK: full_bible.db exists
) else (
    echo ERROR: full_bible.db missing
)
echo.
pause
goto MAIN

:GITHUB_UPLOAD
cls
echo GitHub APK Build Upload
echo ========================
echo.
echo Windows cannot build APK directly!
echo Use GitHub Actions for cloud building
echo.
echo Steps:
echo.
echo 1. Create new repository on GitHub.com
echo    - Repository name: bible-mp3-player
echo    - Set as Public (for free Actions)
echo.
echo 2. Run these commands in Git Bash:
echo    git init
echo    git add .
echo    git commit -m "Ready for APK build"
echo    git remote add origin https://github.com/USERNAME/bible-mp3-player.git
echo    git push -u origin main
echo.
echo 3. Check GitHub repository Actions tab
echo    - APK will be built automatically (10-20 minutes)
echo    - Download APK from Artifacts
echo.
echo TIP: Install Git from https://git-scm.com if needed
echo.
pause
goto MAIN

:HELP
cls
echo Help
echo ====
echo.
echo Option Details:
echo.
echo 1. GUI Launcher (Recommended!)
echo    - Korean text support without corruption
echo    - Access to all apps
echo    - Most stable execution method
echo.
echo 2. OneDrive Integrated App
echo    - Cloud streaming MP3 playback
echo    - OneDrive integration features
echo    - Internet connection required
echo.
echo 3. Basic Local App
echo    - Local files only
echo    - Works offline
echo    - Basic MP3 playback features
echo.
echo 4. Main App
echo    - Default execution file
echo    - Same as OneDrive app
echo.
echo 5. System Check
echo    - Python and package installation status
echo    - File existence verification
echo    - Problem diagnosis tool
echo.
echo 6. GitHub Upload Guide
echo    - Android APK build method
echo    - GitHub Actions usage
echo    - Step-by-step detailed instructions
echo.
echo ERROR Solutions:
echo    - Use option 5 for system status check
echo    - Run: pip install kivy requests
echo    - Verify full_bible.db file exists
echo.
pause
goto MAIN

:INVALID_CHOICE
cls
echo ERROR: Invalid choice!
echo Please enter a number between 0-7.
echo.
pause
goto MAIN

:EXIT
cls
echo Goodbye! Thank you for using Bible MP3 Player.
echo.
pause
exit /b 0