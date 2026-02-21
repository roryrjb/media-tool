uv venv
call .venv\Scripts\activate
uv pip install -r requirements.txt
uv run pyinstaller --onefile --name media-tool media-tool.py
