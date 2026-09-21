from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama

app = FastAPI(
    title="CuraVision AI Backend",
    description="Unified API serving Predictive Chronic Disease Risk & Grounded Medical RAG",
    version="1.0.0"
)

# 1. Load Trained Tabular Model
model = joblib.load("data/diabetes_model.joblib")

# 2. Connect to ChromaDB & Local Ollama LLM
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vector_db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
llm = Ollama(model="llama3.2:3b", temperature=0.0)

# Expected 10 model features
MODEL_COLUMNS = [
    'gender', 'age', 'hypertension', 'heart_disease', 'bmi', 
    'HbA1c_level', 'blood_glucose_level', 
    'smoking_history_current', 'smoking_history_former', 'smoking_history_never'
]

# 3. Input Schemas
class VitalsInput(BaseModel):
    gender: int                   # 0 for Female, 1 for Male
    age: float
    hypertension: int             # 0 or 1
    heart_disease: int            # 0 or 1
    bmi: float
    HbA1c_level: float
    blood_glucose_level: float
    smoking_history: str          # "never", "current", or "former"

class MedicalQueryInput(BaseModel):
    question: str

# --- Endpoints ---

@app.get("/")
def health_check():
    return {"status": "online", "system": "CuraVision AI Core Engine"}

@app.post("/predict-risk")
def predict_risk(data: VitalsInput):
    try:
        # Construct feature dictionary
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

        # Build DataFrame aligned with the exact 10 training features
        input_df = pd.DataFrame([row])[MODEL_COLUMNS]

        prediction = int(model.predict(input_df)[0])
        probability = float(model.predict_proba(input_df)[0][1])

        return {
            "prediction": prediction,
            "status": "High Risk" if prediction == 1 else "Low Risk",
            "risk_score": round(probability, 4)
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