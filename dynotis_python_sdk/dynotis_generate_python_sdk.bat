@echo off
echo ========================================================
echo      DYNOTIS PYTHON SDK GENERATOR
echo ========================================================

:: 1. Navigate to the script's directory (Reliable method)
cd /d "%~dp0"

:: --- SETTINGS ---

:: Proto file is located one level up (../Protos)
SET PROTO_PATH=../Protos

:: Output directory ('generated' folder next to the script)
SET OUT_DIR=./generated

:: --- CLEANUP ---
if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"

:: --- CODE GENERATION ---
echo [PYTHON] Generating code...

:: Run protoc (If grpcio-tools is missing, this will error out)
python -m grpc_tools.protoc -I%PROTO_PATH% --python_out=%OUT_DIR% --grpc_python_out=%OUT_DIR% %PROTO_PATH%/DynotisAPI.proto

:: --- FIXES ---

:: Fix Python relative import error (Common protoc issue)
if exist "%OUT_DIR%\DynotisAPI_pb2_grpc.py" (
    powershell -Command "(Get-Content %OUT_DIR%/DynotisAPI_pb2_grpc.py) -replace 'import DynotisAPI_pb2', 'from . import DynotisAPI_pb2' | Set-Content %OUT_DIR%/DynotisAPI_pb2_grpc.py"
    echo [PYTHON] Import error fixed.
) else (
    echo [ERROR] Files could not be generated. Please ensure 'pip install grpcio-tools' is installed.
)

:: Add __init__.py (To make it a valid Python package)
type NUL > "%OUT_DIR%/__init__.py"

echo.
echo [SUCCESS] Python SDK updated.
pause
