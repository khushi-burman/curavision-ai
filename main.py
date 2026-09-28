import os
import threading

# Set httpx/requests timeouts at the process level before initializing LangChain
os.environ["OLLAMA_TIMEOUT"] = "300"

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama

app = FastAPI(
    title="CuraVision AI Backend",
    description="Unified API serving Predictive Chronic Disease Risk, Grounded Medical RAG, & Integrated Skin Analysis",
    version="1.0.0"
)

# 1. Load Trained Tabular Model
model = joblib.load("data/diabetes_model.joblib")

# 2. Connect to ChromaDB & Local Ollama LLM
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vector_db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# Pass ONLY valid Pydantic fields accepted by Ollama
# - num_predict caps the answer length so generation finishes faster
# - num_ctx keeps the context window small (less memory / faster on a 3B model)
# - keep_alive keeps the model loaded in memory between requests (no cold starts)
# If your langchain-community version rejects `keep_alive`, just remove that line.
llm = Ollama(
    model="llama3.2:3b",
    temperature=0.0,
    timeout=300,
    num_predict=400,
    num_ctx=4096,
    keep_alive="30m",
)


def _warm_up_llm():
    """Loads the model into Ollama's memory so the first real request is fast."""
    try:
        llm.invoke("Reply with the single word: ready")
        print("[startup] Ollama model warmed up.")
    except Exception as exc:
        print(f"[startup] Ollama warm-up skipped: {exc}")


@app.on_event("startup")
def on_startup():
    # Run in a background thread so the API starts immediately
    threading.Thread(target=_warm_up_llm, daemon=True).start()


# Expected 10 model features
MODEL_COLUMNS = [
    'gender', 'age', 'hypertension', 'heart_disease', 'bmi',
    'HbA1c_level', 'blood_glucose_level',
    'smoking_history_current', 'smoking_history_former', 'smoking_history_never'
]

# 3. Input Schemas
class VitalsInput(BaseModel):
    gender: int                  # 0 for Female, 1 for Male
    age: float
    hypertension: int            # 0 or 1
    heart_disease: int           # 0 or 1
    bmi: float
    HbA1c_level: float
    blood_glucose_level: float
    smoking_history: str         # "never", "current", or "former"

class MedicalQueryInput(BaseModel):
    question: str

class IntegratedDiagnosisInput(BaseModel):
    vision_prediction: str
    confidence: float
    symptom_description: str


# --- Endpoints ---

@app.get("/")
def health_check():
    return {"status": "online", "system": "CuraVision AI Core Engine"}


@app.post("/predict-risk")
def predict_risk(data: VitalsInput):
    try:
        row = {
            'gender': data.gender,
            'age': data.age,
            'hypertension': data.hypertension,
            'heart_disease': data.heart_disease,
            'bmi': data.bmi,
            'HbA1c_level': data.HbA1c_level,
            'blood_glucose_level': data.blood_glucose_level,
            'smoking_history_current': 1 if data.smoking_history.lower() == "current" else 0,
            'smoking_history_former': 1 if data.smoking_history.lower() == "former" else 0,
            'smoking_history_never': 1 if data.smoking_history.lower() == "never" else 0,
        }

        input_df = pd.DataFrame([row])[MODEL_COLUMNS]

        prediction = int(model.predict(input_df)[0])
        probability = float(model.predict_proba(input_df)[0][1])
        status = "High Risk" if prediction == 1 else "Low Risk"

        explanation_prompt = f"""
        You are CuraVision AI, an empathetic clinical risk assessment assistant.
        A patient just completed a chronic metabolic screening with these findings:
        - Overall Status: {status} (Predicted Risk Probability: {probability * 100:.1f}%)
        - Patient Profile: Age {data.age}, BMI {data.bmi}
        - Vitals & Labs: Blood Glucose {data.blood_glucose_level} mg/dL, HbA1c {data.HbA1c_level}%
        - Medical History: Hypertension: {'Yes' if data.hypertension else 'No'}, Heart Disease: {'Yes' if data.heart_disease else 'No'}, Smoking: {data.smoking_history}

        Provide a concise, patient-friendly summary formatted strictly in Markdown:
        1. **Assessment Breakdown**: In 2-3 sentences, explain what these specific numbers mean and what factors contributed most to this risk score.
        2. **Recommended Action Steps**: Provide 3 clear, actionable bullet points that the patient can take or discuss with their healthcare provider.
        """

        clinical_notes = llm.invoke(explanation_prompt).strip()

        return {
            "prediction": prediction,
            "status": status,
            "risk_score": round(probability, 4),
            "explanation": clinical_notes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clinical-rag-chat")
def clinical_rag_chat(query: MedicalQueryInput):
    try:
        results = vector_db.similarity_search(query.question, k=2)
        context_text = "\n\n".join([doc.page_content.strip() for doc in results])

        prompt = f"""
        You are the CuraVision AI medical assistant.
        Answer the user's question STRICTLY based on the provided clinical context below.
        Do not speculate. If the answer cannot be found, state that you do not have enough information.

        Context:
        {context_text}

        Question:
        {query.question}

        Grounded Clinical Answer:
        """

        response = llm.invoke(prompt)

        return {
            "query": query.question,
            "clinical_response": response.strip(),
            "retrieved_context": [doc.page_content.strip() for doc in results]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/integrated-diagnosis")
def analyze_integrated_diagnosis(data: IntegratedDiagnosisInput):
    try:
        symptoms_str = data.symptom_description.strip() if data.symptom_description.strip() else "No specific symptoms reported."

        prompt = f"""
        You are CuraVision AI, an empathetic clinical decision support assistant specializing in multi-modal dermatology screening.
        Synthesize the following patient observations:

        1. **Vision Model Finding**: Predicted class as "{data.vision_prediction}" with a confidence score of {data.confidence * 100:.2f}%.
        2. **Patient Reported Symptoms**: "{symptoms_str}"

        Provide a clear, structured clinical assessment formatted in Markdown.
        Keep the whole response under 250 words.
        1. **Clinical Correlation**: Synthesize how the self-reported physical symptoms align with or contextualize the vision model's predicted classification.
        2. **Warning Signs & Monitoring**: Highlight key changes or red flags the patient should observe (e.g., asymmetry, color variation, changes in sensation).
        3. **Next Steps**: Provide practical advice on seeking clinical confirmation from a dermatologist or healthcare provider.
        """

        response = llm.invoke(prompt)

        return {
            "status": "success",
            "vision_prediction": data.vision_prediction,
            "confidence": data.confidence,
            "diagnosis_report": response.strip()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))