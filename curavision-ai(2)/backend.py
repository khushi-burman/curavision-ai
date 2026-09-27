import os
from typing import Any
import requests

DEFAULT_BACKEND_URL = "http://127.0.0.1:8000"
# Increased global default timeout for LLM and vision calls
DEFAULT_TIMEOUT = 300  


def backend_url() -> str:
    return os.getenv("CURAVISION_BACKEND_URL", DEFAULT_BACKEND_URL).rstrip("/")


def post_json(path: str, payload: dict[str, Any], timeout: int = DEFAULT_TIMEOUT) -> dict[str, Any]:
    response = requests.post(f"{backend_url()}{path}", json=payload, timeout=300)
    response.raise_for_status()
    return response.json()


def predict_chronic_risk(payload: dict[str, Any]) -> dict[str, Any]:
    return post_json("/predict-risk", payload)


def predict_integrated_diagnosis(
    vision_prediction: str, confidence: float, symptom_description: str, timeout: int = 300
) -> dict[str, Any]:
    """Sends vision prediction and user symptom text to the FastAPI multi-modal analysis endpoint."""
    payload = {
        "vision_prediction": vision_prediction,
        "confidence": confidence,
        "symptom_description": symptom_description,
    }
    # Set to 300 seconds (5 minutes) to give Ollama enough time to generate the report
    return post_json("/analyze/integrated-diagnosis", payload, timeout=timeout)


def clinical_chat(question: str, timeout: int = 300) -> dict[str, Any]:
    # Sends both keys so it works regardless of whether FastAPI expects "query" or "question"
    raw_response = post_json(
        "/clinical-rag-chat", 
        {"query": question, "question": question}, 
        timeout=timeout
    )
    
    # Map the returned text to "clinical_response" so assistant.py can render it
    reply_text = raw_response.get("clinical_response") or raw_response.get("response") or "No answer was returned."
    return {"clinical_response": reply_text}