python -m venv venv
call venv\Scripts\activate
call pip install -r requirements.txt
call pyinstaller --onefile --name media-tool media-tool.py
