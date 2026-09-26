import os
from typing import Any
import requests

DEFAULT_BACKEND_URL = "http://127.0.0.1:8000"


def backend_url() -> str:
    return os.getenv("CURAVISION_BACKEND_URL", DEFAULT_BACKEND_URL).rstrip("/")


def post_json(path: str, payload: dict[str, Any], timeout: int = 120) -> dict[str, Any]:
    response = requests.post(f"{backend_url()}{path}", json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()


def predict_chronic_risk(payload: dict[str, Any]) -> dict[str, Any]:
    return post_json("/predict-risk", payload)


def clinical_chat(question: str) -> dict[str, Any]:
    # Sends both keys so it works regardless of whether FastAPI expects "query" or "question"
    raw_response = post_json("/clinical-rag-chat", {"query": question, "question": question}, timeout=180)
    
    # Map the returned text to "clinical_response" so assistant.py can render it
    reply_text = raw_response.get("clinical_response") or raw_response.get("response") or "No answer was returned."
    return {"clinical_response": reply_text}

