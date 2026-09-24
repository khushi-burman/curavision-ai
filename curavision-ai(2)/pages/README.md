# 🩺 CuraVision AI

CuraVision AI is a comprehensive, multi-modal **Clinical Decision Support System (CDSS)** designed to assist healthcare providers with diagnostic insights and continuous patient care management.

## 🌟 Key Features

* 🔬 **Skin Disease Detection (Vision AI): ** Automated detection and classification of skin lesions and dermatological conditions using computer vision models.
* 📈 **Longitudinal Health Tracking: ** Time-series monitoring of continuous patient metrics (Blood Pressure, Blood Sugar/Glucose) to identify risk trends over time.
* 🧠 **Medical RAG & Guideline Retrieval: ** Local vector search powered by `ChromaDB` and `nomic-embed-text` to query verified clinical practice guidelines.
* 🤖 **Clinical Reasoning Engine: ** Local LLM integration via `Llama 3.2` (Ollama) to synthesize patient history, current vitals, and vision model outputs into actionable medical assessments.
* ⚡ **Production-Ready REST APIs: ** Modular backend built with `FastAPI` for fast, asynchronous request handling.
