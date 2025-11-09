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

def answer_from_context(question: str, context_chunks: List[dict], model: str = "llama/8b", temperature: float = 0.0, max_tokens: int = 512):
    """
    context_chunks: list of dicts with keys {chunk_id, text, source, page}
    Returns: text (string)
    """
    if not is_ollama_available():
        raise EnvironmentError("Ollama is not available on PATH. Install Ollama and pull a model.")

    system = _build_system_prompt()
    # Build context text by joining top chunks with their chunk ids
    ctx_parts = []
    for c in context_chunks:
        cid = c.get("chunk_id", c.get("id", ""))
        src = c.get("source", "")
        page = c.get("page", "")
        snippet = c.get("text", "").strip().replace("\n", " ")
        ctx_parts.append(f"[{cid}] (source: {src} page: {page})\n{snippet}\n")

    # Keep the prompt reasonably sized (truncate if too many chunks)
    context_text = "\n---\n".join(ctx_parts[:8])

    prompt = f"""<system>\n{system}\n</system>\n\n<user>\nContext:\n{context_text}\n\nQuestion: {question}\n\nAnswer concisely and list chunk citations used (e.g., [abc123-p1-c0]).\n</user>"""

    # Call ollama CLI: ollama generate <model> --prompt "<prompt>"
    # Use subprocess to avoid shell quoting issues
    try:
        proc = subprocess.run([OLLAMA_CMD, "generate", model, "--prompt", prompt, "--temperature", str(temperature), "--max-tokens", str(max_tokens)],
                              capture_output=True, text=True, timeout=60)
        if proc.returncode != 0:
            # Try a fallback: call without --prompt and pass via stdin
            raise RuntimeError(proc.stderr)
        output = proc.stdout.strip()
        # Ollama sometimes returns JSON or raw text; we return raw text here
        return output
    except Exception as e:
        # Re-raise with helpful message
        raise RuntimeError(f"Ollama generation failed: {e}")
