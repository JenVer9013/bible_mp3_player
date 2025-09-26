@echo off
chcp 65001 > nul
color 0B
title 성경 MP3 플레이어

:MAIN
cls
echo ══════════════════════════════════════════════════
echo             🎵 성경 MP3 플레이어 🎵
echo ══════════════════════════════════════════════════
echo.
echo 📋 실행할 프로그램을 선택하세요:
echo.
echo   1️⃣  GUI 런처 실행 (한글 지원, 추천!)
echo   2️⃣  OneDrive 통합 앱 실행
echo   3️⃣  기본 로컬 앱 실행
echo   4️⃣  메인 앱 실행
echo   5️⃣  시스템 상태 확인
echo   6️⃣  GitHub에 APK 빌드용 업로드
echo   7️⃣  도움말 보기
echo   0️⃣  종료
echo.
echo ══════════════════════════════════════════════════
set /p choice="선택 (0-7): "

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
echo 🚀 GUI 런처 실행 중...
echo ═══════════════════════════════════
echo 📌 한글 깨짐 방지 GUI 런처를 실행합니다
echo 💡 이 방법이 가장 안정적입니다!
echo.
python gui_launcher.py
if errorlevel 1 (
    echo.
    echo ❌ GUI 런처 실행 중 오류가 발생했습니다
    echo 💡 pip install kivy requests 명령으로 의존성을 설치하세요
    pause
)
goto MAIN

:ONEDRIVE_APP
cls
echo 🌐 OneDrive 통합 앱 실행 중...
echo ═══════════════════════════════════
echo 📌 OneDrive 클라우드 스트리밍 기능 포함
echo 💡 인터넷 연결이 필요합니다
echo.
python kivy_onedrive_main.py
if errorlevel 1 (
    echo.
    echo ❌ OneDrive 앱 실행 중 오류가 발생했습니다
    pause
)
goto MAIN

:LOCAL_APP
cls
echo 💾 기본 로컬 앱 실행 중...
echo ═══════════════════════════════════
echo 📌 로컬 파일만 사용하는 기본 버전
echo 💡 오프라인에서도 작동합니다
echo.
python kivy_main.py
if errorlevel 1 (
    echo.
    echo ❌ 로컬 앱 실행 중 오류가 발생했습니다
    pause
)
goto MAIN

:MAIN_APP
cls
echo 🎯 메인 앱 실행 중...
echo ═══════════════════════════════════
echo 📌 기본 메인 실행 파일
echo.
python main.py
if errorlevel 1 (
    echo.
    echo ❌ 메인 앱 실행 중 오류가 발생했습니다
    pause
)
goto MAIN

:SYSTEM_CHECK
cls
echo 🔍 시스템 상태 확인 중...
echo ═══════════════════════════════════
echo.
echo 📌 Python 버전:
python --version
echo.
echo 📌 현재 폴더 파일 목록:
dir /b *.py *.db *.spec *.txt
echo.
echo 📌 필수 Python 패키지 확인:
echo Kivy 설치 상태:
python -c "import kivy; print('✅ Kivy:', kivy.__version__)" 2>nul || echo "❌ Kivy 미설치"
echo Requests 설치 상태:
python -c "import requests; print('✅ Requests:', requests.__version__)" 2>nul || echo "❌ Requests 미설치"
echo SQLite3 설치 상태:
python -c "import sqlite3; print('✅ SQLite3: 설치됨')" 2>nul || echo "❌ SQLite3 미설치"
echo.
echo 📌 데이터베이스 파일:
if exist "full_bible.db" (
    echo ✅ full_bible.db 존재
) else (
    echo ❌ full_bible.db 누락
)
echo.
pause
goto MAIN

:GITHUB_UPLOAD
cls
echo 📱 GitHub APK 빌드용 업로드
echo ═══════════════════════════════════
echo.
echo 📌 Windows에서는 APK를 직접 빌드할 수 없습니다!
echo 💡 GitHub Actions를 사용해서 클라우드에서 빌드합니다
echo.
echo 🚀 다음 단계를 따라하세요:
echo.
echo 1️⃣  GitHub.com에서 새 저장소 생성
echo    - 저장소 이름: bible-mp3-player
echo    - Public으로 설정 (무료 Actions 사용)
echo.
echo 2️⃣  Git Bash에서 다음 명령어 실행:
echo    git init
echo    git add .
echo    git commit -m "APK 빌드 준비"
echo    git remote add origin https://github.com/사용자명/bible-mp3-player.git
echo    git push -u origin main
echo.
echo 3️⃣  GitHub 저장소 → Actions 탭에서 빌드 확인
echo    - 10-20분 후 완성된 APK 다운로드
echo.
echo 💡 Git이 설치되지 않은 경우:
echo    https://git-scm.com에서 Git 다운로드
echo.
pause
goto MAIN

:HELP
cls
echo 📖 도움말
echo ═══════════════════════════════════
echo.
echo 🎯 각 옵션 설명:
echo.
echo 1️⃣  GUI 런처 (추천!)
echo    - 한글 깨짐 없는 그래픽 인터페이스
echo    - 모든 앱에 접근 가능
echo    - 가장 안정적인 실행 방법
echo.
echo 2️⃣  OneDrive 통합 앱
echo    - 클라우드 스트리밍 MP3 재생
echo    - OneDrive 연동 기능
echo    - 인터넷 연결 필요
echo.
echo 3️⃣  기본 로컬 앱
echo    - 로컬 파일만 사용
echo    - 오프라인 실행 가능
echo    - 기본 MP3 재생 기능
echo.
echo 4️⃣  메인 앱
echo    - 기본 실행 파일
echo    - OneDrive 앱과 동일
echo.
echo 5️⃣  시스템 상태 확인
echo    - Python 및 패키지 설치 상태
echo    - 파일 존재 여부 확인
echo    - 문제 진단 도구
echo.
echo 6️⃣  GitHub 업로드 가이드
echo    - Android APK 빌드 방법
echo    - GitHub Actions 사용법
echo    - 단계별 상세 안내
echo.
echo ❌ 문제 발생시:
echo    - 5번으로 시스템 상태 확인
echo    - pip install kivy requests 실행
echo    - full_bible.db 파일 존재 확인
echo.
pause
goto MAIN

:INVALID_CHOICE
cls
echo ❌ 잘못된 선택입니다!
echo 0-7 사이의 숫자를 입력하세요.
echo.
pause
goto MAIN

:EXIT
cls
echo 👋 성경 MP3 플레이어를 종료합니다.
echo 감사합니다! 🙏
echo.
pause
exit /b 0