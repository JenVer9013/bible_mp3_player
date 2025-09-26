@echo off
echo Updating GitHub repository with fixes...
echo.

echo Adding modified files...
git add .

echo Committing changes...
git commit -m "Fix requirements.txt - Remove tkinter and sqlite3 (standard library)"

echo Pushing to GitHub...
git push

echo.
echo GitHub update completed!
echo Now you can go to Actions tab and run the workflow manually.
echo.
pause