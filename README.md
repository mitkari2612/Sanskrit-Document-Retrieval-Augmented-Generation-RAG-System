# Sanskrit Document RAG System

A local Retrieval-Augmented Generation (RAG) application for querying the Bhagavad Gita using a Streamlit interface.

## Project Structure

- `code/`
  - `app.py` - Streamlit web application frontend
  - `generator.py` - LLM generator wrapper for Ollama and HuggingFace Transformers
  - `ingest.py` - Data ingestion pipeline for the Bhagavad Gita corpus
  - `rag_pipeline.py` - Retrieval + generation pipeline coordinator
  - `retriever.py` - TF-IDF and optional semantic retriever
  - `requirements.txt` - Python package dependencies
- `data/`
  - `gita_processed.json` - Processed Bhagavad Gita corpus used for retrieval
- `report/`
  - `generate_report.py` - Report generation script

## Setup

1. Open PowerShell.
2. Change to the project folder:
   ```powershell
   cd "C:\Users\Ajay Mitkari\Downloads\Project Nagpur\RAG_Sanskrit_Ajay_Mitkari"
   ```
3. (Optional) create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   & ".venv\Scripts\Activate.ps1"
   ```
4. Install dependencies:
   ```powershell
   python -m pip install -r code\requirements.txt
   ```

## Running the app

Start the Streamlit app from the project root:

```powershell
cd "C:\Users\Ajay Mitkari\Downloads\Project Nagpur\RAG_Sanskrit_Ajay_Mitkari"
& ".venv\Scripts\python.exe" -m streamlit run code\app.py
```

Then open the browser at:

- `http://localhost:8501`

## How to use

1. In the left sidebar, choose the generator backend:
   - `ollama` if you have Ollama installed and running locally
   - `transformers` for a Python-based local model
2. Set the model name:
   - `qwen2.5:0.5b` for Ollama
   - `Qwen/Qwen2.5-0.5B-Instruct` for Transformers
3. Enter a query in Sanskrit, transliteration, or English.
4. Click **Search the Gita**.
5. The app will show retrieved verses and a generated answer.

## Notes

- If the generated answer section shows an error, it means the model backend is not available.
- For local Python inference, use `transformers` and install the required packages.
- The app currently supports fallback from Ollama to Transformers when Ollama is unavailable.

## GitHub Upload

To upload this project to GitHub:

1. Create a new repository on GitHub.
2. In this folder, run:
   ```powershell
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/USERNAME/REPO_NAME.git
   git push -u origin main
   ```

Replace `USERNAME` and `REPO_NAME` with your GitHub account and repository name.
