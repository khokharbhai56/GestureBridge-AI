# routes/sign_demo.py
from fastapi import APIRouter
from backend.sign_model.final_pred import predict_sign

router = APIRouter()

@router.get("/sign-language/predict")
def get_sign_prediction():
    result = predict_sign()
    return {"prediction": result}
