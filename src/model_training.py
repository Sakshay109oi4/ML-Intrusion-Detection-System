"""
Phase 4: Model Training
Train and compare Random Forest, Decision Tree, Logistic Regression, and SVM.
"""

import json
from datetime import datetime

from sklearn.calibration import CalibratedClassifierCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC

from config.config import BEST_MODEL_PATH, METRICS_DIR, MODELS_DIR, MODEL_CONFIGS
from src.utils import save_artifact, setup_directories, setup_logging

logger = setup_logging("ModelTraining")


def get_classifier(name: str):
    """Instantiate classifier by configuration key."""
    config = MODEL_CONFIGS[name]
    class_name = config["classifier"]
    params = config["params"]

    mapping = {
        "RandomForestClassifier": RandomForestClassifier,
        "DecisionTreeClassifier": DecisionTreeClassifier,
        "LogisticRegression": LogisticRegression,
        "LinearSVC": LinearSVC,
    }
    if class_name not in mapping:
        raise ValueError(f"Unknown classifier: {class_name}")
    return mapping[class_name](**params)


def train_single_model(name: str, X_train, y_train):
    """Train one model and persist to disk."""
    logger.info("Training %s ...", name)
    model = get_classifier(name)
    model.fit(X_train, y_train)

    model_path = MODELS_DIR / f"{name}_model.joblib"
    save_artifact(model, model_path)
    logger.info("Saved model: %s", model_path)
    return model


def train_all_models(X_train, y_train) -> dict:
    """
    Train all four classifiers and return fitted models.

    Returns
    -------
    dict
        Model name -> fitted estimator
    """
    setup_directories()
    models = {}
    for name in MODEL_CONFIGS:
        models[name] = train_single_model(name, X_train, y_train)

    metadata = {
        "trained_at": datetime.now().isoformat(),
        "models": list(MODEL_CONFIGS.keys()),
        "train_samples": int(len(y_train)),
        "features": int(X_train.shape[1]),
    }
    meta_path = MODELS_DIR / "training_metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    logger.info("All models trained successfully.")
    return models


def select_best_model(results: dict) -> tuple[str, object]:
    """
    Select best model by weighted F1 score from evaluation results.

    Parameters
    ----------
    results : dict
        Output from evaluation.evaluate_all_models()

    Returns
    -------
    tuple[str, object]
        Best model name and loaded model object.
    """
    best_name = max(results, key=lambda k: results[k]["f1_weighted"])
    best_model = results[best_name]["model"]
    save_artifact(best_model, BEST_MODEL_PATH)
    logger.info("Best model: %s (F1=%.4f)", best_name, results[best_name]["f1_weighted"])
    return best_name, best_model


def wrap_svm_for_proba(model):
    """
    Wrap LinearSVC with probability calibration for ROC curves.
    Used only when probability estimates are needed at inference.
    """
    return CalibratedClassifierCV(model, cv=3)


if __name__ == "__main__":
    from src.data_cleaning import prepare_datasets

    data = prepare_datasets()
    train_all_models(data["X_train"], data["y_train"])
