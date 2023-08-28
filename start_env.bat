@echo off
if not exist "travelenv\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    pause
    exit
)
call travelenv\Scripts\activate.bat

if not exist "main.py" (
    echo Error: main.py not found!
    pause
    exit
)
python main.py
cmd /k
