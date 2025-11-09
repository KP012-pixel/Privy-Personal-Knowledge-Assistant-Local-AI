# Privy — Local Personal Knowledge Assistant

**Local-first** knowledge assistant using local LLMs + embeddings.

## Quick start (Linux / WSL / macOS)

1. Clone repo and create venv:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
2. Install Ollama and pull a model (example names; follow Ollama docs):
```bash
# Install Ollama (official instructions: https://ollama.com/docs)
ollama pull llama/8b   # or the exact model you want (LLaMA 3 8B if available)
```
3. Run Streamlit:
```bash
streamlit run ui/streamlit_app.py
Open http://localhost:8501
```
## Files

- backend/ — ingestion, embeddings, vectorstore, llm wrapper

- ui/ — Streamlit app

## Notes

- This repo uses local models. For best accuracy pick a high-quality 8B model you have resources for.

- Tesseract OCR must be installed on your system for OCR (Linux: sudo apt install tesseract-ocr).
