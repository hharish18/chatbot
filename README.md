# Smart Retrieval-Based Chatbot

A complete offline-friendly chatbot using Flask, SQLite, TF-IDF, and cosine similarity.

## Run on Windows

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:SECRET_KEY = "use-a-random-value-here"
python app.py
```

Open http://127.0.0.1:5000. The admin panel is at http://127.0.0.1:5000/admin.

## Optional ChatGPT-style answers

To answer questions outside the local knowledge base, set an OpenAI-compatible API key before starting Flask:

```powershell
$env:OPENAI_API_KEY = "your-api-key"
C:/Python314/python.exe app.py
```

The app uses `gpt-4o-mini` by default. You can set `OPENAI_MODEL` and `OPENAI_API_URL` for another compatible provider. Without a key, the app stays offline and uses the knowledge base plus its fallback response.

Default development login: `admin` / `admin123`. Set `ADMIN_USERNAME` and `ADMIN_PASSWORD` before deployment.

## Features

- TF-IDF and cosine-similarity retrieval
- SQLite knowledge base and chat history
- Fallback responses below a configurable similarity threshold
- Admin login, question creation, and deletion
- No external API key required
