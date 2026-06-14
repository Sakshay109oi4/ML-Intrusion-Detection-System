"""
Phase 6: Prediction Module
Load saved model and predict intrusion category from network features.
"""

import pandas as pd
import numpy as np

from config.config import (
    BEST_MODEL_PATH,
    CATEGORICAL_COLUMNS,
    COLUMN_NAMES,
    FEATURE_NAMES_PATH,
    LABEL_ENCODER_PATH,
    MODELS_DIR,
    PREPROCESSOR_PATH,
    TARGET_CLASSES,
)
from src.utils import load_artifact, setup_logging

logger = setup_logging("Prediction")


def get_default_feature_template() -> dict:
    """
    Return a dictionary of default NSL-KDD feature values for demo/testing.
    Keys match raw (pre-encoding) column names.
    """
    numeric_cols = [
        c for c in COLUMN_NAMES
        if c not in CATEGORICAL_COLUMNS + ["label", "difficulty"]
    ]
    template = {col: 0 for col in numeric_cols}
    template.update({"protocol_type": "tcp", "service": "http", "flag": "SF"})
    return template


def load_prediction_artifacts(model_name: str | None = None):
    """
    Load model, preprocessor, and label encoder.

    Parameters
    ----------
    model_name : str, optional
        One of: random_forest, decision_tree, logistic_regression, svm.
        Defaults to best saved model.
    """
    if model_name:
        model_path = MODELS_DIR / f"{model_name}_model.joblib"
    else:
        model_path = BEST_MODEL_PATH
        if not model_path.exists():
            model_path = MODELS_DIR / "random_forest_model.joblib"

    model = load_artifact(model_path)
    preprocessor = load_artifact(PREPROCESSOR_PATH)
    label_encoder = load_artifact(LABEL_ENCODER_PATH)
    return model, preprocessor, label_encoder


def validate_input(features: dict) -> pd.DataFrame:
    """Validate and convert user input dict to DataFrame row."""
    feature_cols = [
        c for c in COLUMN_NAMES if c not in ["label", "difficulty"]
    ]
    missing = [c for c in feature_cols if c not in features]
    if missing:
        raise ValueError(f"Missing required features: {missing}")

    row = {col: features.get(col, 0) for col in feature_cols}
    return pd.DataFrame([row])


def predict(features: dict, model_name: str | None = None) -> dict:
    """
    Predict attack category from raw network feature dictionary.

    Parameters
    ----------
    features : dict
        Raw NSL-KDD feature values (41 features).

    Returns
    -------
    dict
        prediction, confidence, probabilities, class labels
    """
    model, preprocessor, label_encoder = load_prediction_artifacts(model_name)
    df = validate_input(features)
    X = preprocessor.transform(df)
    prediction_idx = model.predict(X)[0]

    result = {
        "prediction": label_encoder.inverse_transform([prediction_idx])[0],
        "prediction_index": int(prediction_idx),
    }

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0]
        result["confidence"] = float(proba[prediction_idx])
        result["probabilities"] = {
            label_encoder.classes_[i]: float(proba[i])
            for i in range(len(label_encoder.classes_))
        }
    elif hasattr(model, "decision_function"):
        scores = model.decision_function(X)[0]
        if np.ndim(scores) == 0:
            scores = np.array([-scores, scores])
        exp_s = np.exp(scores - np.max(scores))
        proba = exp_s / exp_s.sum()
        result["confidence"] = float(proba[prediction_idx])
        result["probabilities"] = {
            label_encoder.classes_[i]: float(proba[i])
            for i in range(len(label_encoder.classes_))
        }
    else:
        result["confidence"] = 1.0
        result["probabilities"] = {result["prediction"]: 1.0}

    return result


def predict_batch(df: pd.DataFrame, model_name: str | None = None) -> pd.DataFrame:
    """Predict on multiple rows."""
    model, preprocessor, label_encoder = load_prediction_artifacts(model_name)
    feature_cols = [c for c in COLUMN_NAMES if c not in ["label", "difficulty"]]
    X = preprocessor.transform(df[feature_cols])
    preds = model.predict(X)
    df = df.copy()
    df["predicted_category"] = label_encoder.inverse_transform(preds)
    return df


def format_prediction_result(result: dict) -> str:
    """Human-readable prediction output."""
    lines = [
        f"Prediction: {result['prediction']}",
        f"Confidence: {result['confidence']:.2%}",
        "",
        "Class Probabilities:",
    ]
    for cls, prob in sorted(result["probabilities"].items(), key=lambda x: -x[1]):
        lines.append(f"  {cls}: {prob:.2%}")
    return "\n".join(lines)


if __name__ == "__main__":
    sample = get_default_feature_template()
    sample["dst_bytes"] = 0
    sample["serror_rate"] = 1.0
    sample["flag"] = "S0"
    out = predict(sample)
    print(format_prediction_result(out))
