import subprocess
import json
import shutil
from typing import List

OLLAMA_CMD = shutil.which("ollama")

def is_ollama_available():
    return OLLAMA_CMD is not None

def _build_system_prompt():
    return (
        "You are Privy, a concise and professional assistant. Use only the provided context to answer. "
        "If the answer is not in the context, say you cannot find it. "
        "Cite the chunks you used in square brackets like [chunk_id]. Be brief and clear."
    )

def answer_from_context(question: str, context_chunks: List[dict], model: str = "llama3:8b", temperature: float = 0.0, max_tokens: int = 512):
    """
    context_chunks: list of dicts with keys {chunk_id, text, source, page}
    Returns: text (string)
    """
    if not is_ollama_available():
        raise EnvironmentError("Ollama is not available on PATH. Install Ollama and pull a model.")

    system = _build_system_prompt()

    # Build context text
    ctx_parts = []
    for c in context_chunks:
        cid = c.get("chunk_id", c.get("id", ""))
        src = c.get("source", "")
        page = c.get("page", "")
        snippet = c.get("text", "").strip().replace("\n", " ")
        ctx_parts.append(f"[{cid}] (source: {src} page: {page})\n{snippet}\n")

    context_text = "\n---\n".join(ctx_parts[:8])

    # Full prompt to send via stdin
    prompt = f"""<system>
{system}
</system>

<user>
Context:
{context_text}

Question: {question}

Answer concisely and list chunk citations used (e.g., [abc123-p1-c0]).
</user>
"""

    try:
        # NO flags allowed in Ollama 0.12 — use stdin input
        proc = subprocess.run(
            [OLLAMA_CMD, "run", model],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=60,
            encoding="utf-8",
            errors="replace"
        )

        if proc.returncode != 0:
            raise RuntimeError(proc.stderr)

        return proc.stdout.strip()

    except Exception as e:
        raise RuntimeError(f"Ollama generation failed: {e}")
