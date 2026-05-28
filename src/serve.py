from contextlib import asynccontextmanager
from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field

MODEL_PATH = Path("models/churn_model.pkl")

predictions_total = Counter("predictions_total", "Всего предсказаний", ["action"])
prediction_latency = Histogram("prediction_latency_seconds", "Время инференса")

state = {"model": None}


@asynccontextmanager
async def lifespan(app: FastAPI):
    if MODEL_PATH.exists():
        state["model"] = joblib.load(MODEL_PATH)
    yield
    state["model"] = None


app = FastAPI(title="Churn Prediction API", lifespan=lifespan)


class Customer(BaseModel):
    tenure: int = Field(ge=0, le=72)
    monthly_charges: float = Field(ge=0)
    total_charges: float = Field(ge=0)
    contract: int = Field(ge=0, le=2)
    internet_service: int = Field(ge=0, le=2)
    payment_method: int = Field(ge=0, le=3)


class Prediction(BaseModel):
    churn_probability: float
    action: str


def choose_action(proba: float) -> str:
    if proba > 0.7:
        return "urgent_retention_offer"
    if proba > 0.4:
        return "send_discount"
    return "no_action"


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": state["model"] is not None}


@app.post("/predict", response_model=Prediction)
def predict(customer: Customer):
    if state["model"] is None:
        raise HTTPException(status_code=503, detail="Model is not loaded")

    with prediction_latency.time():
        features = [[
            customer.tenure,
            customer.monthly_charges,
            customer.total_charges,
            customer.contract,
            customer.internet_service,
            customer.payment_method,
        ]]
        proba = float(state["model"].predict_proba(features)[0][1])

    action = choose_action(proba)
    predictions_total.labels(action=action).inc()
    return Prediction(churn_probability=proba, action=action)


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
