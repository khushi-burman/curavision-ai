from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI(title="CuraVision Chronic Risk API")

model = joblib.load("data/diabetes_model.joblib")

MODEL_COLUMNS = [
    "gender",
    "age",
    "hypertension",
    "heart_disease",
    "bmi",
    "HbA1c_level",
    "blood_glucose_level",
    "smoking_history_current",
    "smoking_history_former",
    "smoking_history_never",
]

class VitalsInput(BaseModel):
    gender: int
    age: float
    hypertension: int
    heart_disease: int
    bmi: float
    HbA1c_level: float
    blood_glucose_level: float
    smoking_history: str

@app.get("/")
def health_check():
    return {"status": "online"}

@app.post("/predict-risk")
def predict_risk(data: VitalsInput):
    row = {
        "gender": data.gender,
        "age": data.age,
        "hypertension": data.hypertension,
        "heart_disease": data.heart_disease,
        "bmi": data.bmi,
        "HbA1c_level": data.HbA1c_level,
        "blood_glucose_level": data.blood_glucose_level,
        "smoking_history_current": 1 if data.smoking_history.lower() == "current" else 0,
        "smoking_history_former": 1 if data.smoking_history.lower() == "former" else 0,
        "smoking_history_never": 1 if data.smoking_history.lower() == "never" else 0,
    }

    input_df = pd.DataFrame([row])[MODEL_COLUMNS]

    prediction = int(model.predict(input_df)[0])
    probability = float(model.predict_proba(input_df)[0][1])

    return {
        "prediction": prediction,
        "status": "High Risk" if prediction == 1 else "Low Risk",
        "risk_score": round(probability, 4),
    }
