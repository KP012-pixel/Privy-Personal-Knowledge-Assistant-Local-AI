# Privy — Local Personal Knowledge Assistant

A **local-first AI knowledge assistant** that lets you upload documents (PDF, TXT, notes) and turn them into a **searchable personal knowledge base.**
All processing happens **on your device** using **local LLMs + local embeddings.**

## Quick Start (Windows / macOS / Linux)

## 1. Clone the repo
```bash
git clone https://github.com/<your-username>/Privy-Personal-Knowledge-Assistant-Local-AI
cd Privy-Personal-Knowledge-Assistant-Local-AI
```
## 2. Create and activate virtual environment
#### Windows (PowerShell)
```bash
python -m venv .venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1
```
#### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```
## 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

## 4. Install Ollama (required)
Download from:
https://ollama.com/download

After installation, restart the terminal and verify:
```bash
ollama --version
```
## 5. Pull a local model
Recommended:
```bash
ollama pull llama3:8b
```
You may replace with another model supported by your hardware.
## 6. Run the app
```bash
streamlit run ui/streamlit_app.py
```
Then open:
```bash
http://localhost:8501
```
## Features

- Upload PDFs or TXT files

- Automatic document chunking

- Local embeddings (FAISS)

- Query your knowledge base using local LLM

- All processing happens offline, nothing leaves your machine

- Privacy-focused design

## Requirements

- Python 3.10 or newer

- Ollama installed locally

- For PDF OCR:
  - Windows → install Tesseract manually
  - Linux → `sudo apt install tesseract-ocr`
  - macOS → `brew install tesseract`

## Troubleshooting
### 1. `ModuleNotFoundError: No module named 'backend'`
This occurs when Streamlit is executed without the project root in Python’s import path.
#### Windows (PowerShell):
```bash
$env:PYTHONPATH = "$PWD"
streamlit run ui/streamlit_app.py
```
#### macOS / Linux / WSL:
```bash
export PYTHONPATH=$PWD
streamlit run ui/streamlit_app.py
```
### 2. PowerShell does not recognize newly installed tools (e.g., Ollama)
If PowerShell still reports “command not found” after installing a tool:

**1.** Close the terminal

**2.** Close IDE

**3.** Reopen IDE

**4.** Open a new PowerShell terminal

This forces a refresh of the system PATH.
### 3. `Fatal error in launcher: Unable to create process using ... streamlit.exe`
Occurs when Streamlit was installed before the virtual environment existed or VS Code was opened in the wrong directory.

**Fix:**
```bash
pip install --force-reinstall streamlit
streamlit run ui/streamlit_app.py
```
### 4. `tesseract` command not found
OCR features require Tesseract to be installed and available on your PATH.
- **Windows:** Install via the official Tesseract installer
- **Ubuntu/Linux:**
```bash
sudo apt install tesseract-ocr
```
- **macOS:**
```bash
brew install tesseract
```
### 5. Streamlit runs, but documents are not processed
This usually indicates missing dependencies or missing local models.
- Reinstall project dependencies:
```bash
pip install -r requirements.txt
```
- Ensure your Ollama models are installed:
```bash
ollama pull llama3
```
