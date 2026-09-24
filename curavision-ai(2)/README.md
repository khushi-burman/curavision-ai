# CuraVision AI Frontend

Streamlit frontend customized for the supplied CuraVision trained models.

## Model integration

### 1. Chronic-risk model
The UI sends exactly the fields expected by the supplied FastAPI service:
- gender
- age
- hypertension
- heart_disease
- bmi
- HbA1c_level
- blood_glucose_level
- smoking_history

Start the backend and, if needed, set:

`CURAVISION_BACKEND_URL=http://127.0.0.1:8000`

The assistant also uses the backend `/clinical-rag-chat` endpoint.

### 2. Skin-vision model
The UI is prepared for the supplied `inference.py` and its EfficientNet-B4 7-class output. Put the trained weights at:

`models/best_skin_model.pth`

or set `CURAVISION_SKIN_MODEL_PATH` to the actual weights path. The frontend expects the vision model's `inference.py` to be available in `skin_model/` or `model/`.

The uploaded frontend package did not contain the `.pth` weights, so the weights are intentionally not fabricated or included.

## Account flow

- Portal role selection has been removed.
- The encrypted-connection footer text has been removed.
- `Create an account` is now a real Streamlit button that opens `pages/signup.py`.
- New accounts are kept in the current Streamlit session. A production deployment should replace this with a database/authentication service.

## Run

```powershell
pip install -r requirements.txt
streamlit run app.py
```
