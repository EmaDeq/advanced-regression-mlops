"""FastAPI inference application serving a locally trusted model artifact."""

import os
from functools import lru_cache

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from advanced_regression_mlops.config import FEATURES, model_path

app = FastAPI(
    title="Advanced Regression MLOps API",
    version="0.1.0",
    description="Historical Boston Housing regression demo; not for real housing decisions.",
)


class HousingFeatures(BaseModel):
    """12 canonical numerical predictors; racially constructed B is excluded."""

    model_config = ConfigDict(extra="forbid")
    CRIM: float = Field(ge=0)
    ZN: float = Field(ge=0, le=100)
    INDUS: float = Field(ge=0)
    CHAS: int = Field(ge=0, le=1)
    NOX: float = Field(ge=0)
    RM: float = Field(gt=0)
    AGE: float = Field(ge=0, le=100)
    DIS: float = Field(ge=0)
    RAD: float = Field(ge=0)
    TAX: float = Field(ge=0)
    PTRATIO: float = Field(ge=0)
    LSTAT: float = Field(ge=0)


class Prediction(BaseModel):
    predicted_value_thousands_usd: float
    model_version: str
    environment: str


@lru_cache(maxsize=1)
def load_bundle() -> dict:
    path = model_path()
    if not path.is_file():
        raise FileNotFoundError(f"Model artifact not found: {path}")
    # joblib/pickle files can execute code on deserialization; only load models you built.
    bundle = joblib.load(path)
    if bundle.get("features") != list(FEATURES):
        raise ValueError("Model's feature schema does not match API schema")
    return bundle


@app.get("/health")
def health():
    try:
        load_bundle()
    except (FileNotFoundError, ValueError, OSError):
        return JSONResponse(status_code=503, content={"status": "unready"})
    return {"status": "ok", "environment": os.getenv("MLOPS_ENV", "local")}


@app.get("/model-info")
def model_info() -> dict:
    try:
        bundle = load_bundle()
    except (FileNotFoundError, ValueError, OSError) as exc:
        raise HTTPException(status_code=503, detail="Model not ready") from exc
    return {
        "model_version": bundle["version"],
        "features": bundle["features"],
        "target_unit": "thousands of historic USD",
        "warning": "Educational historical benchmark only; not for housing decisions",
    }


@app.post("/predict", response_model=Prediction)
def predict(features: HousingFeatures) -> Prediction:
    try:
        bundle = load_bundle()
    except (FileNotFoundError, ValueError, OSError) as exc:
        raise HTTPException(status_code=503, detail="Model not ready") from exc
    frame = pd.DataFrame([features.model_dump()], columns=list(FEATURES))
    predicted = float(bundle["pipeline"].predict(frame)[0])
    return Prediction(
        predicted_value_thousands_usd=round(predicted, 4),
        model_version=bundle["version"],
        environment=os.getenv("MLOPS_ENV", "local"),
    )
