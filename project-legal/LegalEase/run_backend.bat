@echo off
set "PROJECT_DIR=%~dp0"
pushd "%PROJECT_DIR%"

if exist ".venv\Scripts\activate.bat" (
	call ".venv\Scripts\activate.bat"
) else if exist "..\.venv\Scripts\activate.bat" (
	call "..\.venv\Scripts\activate.bat"
) else (
	echo Could not find a virtual environment in LegalEase\.venv or the parent folder.
	popd
	exit /b 1
)

uvicorn backend.main:app --reload --reload-dir . --host 127.0.0.1 --port 8000
popd
