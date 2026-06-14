"""
Phase 5: Model Evaluation
Accuracy, Precision, Recall, F1, Confusion Matrix, and ROC curves.
"""

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.preprocessing import label_binarize
from sklearn.svm import LinearSVC

from config.config import FIGURES_DIR, METRICS_DIR, MODELS_DIR, MODEL_CONFIGS, TARGET_CLASSES
from src.utils import configure_plot_style, load_artifact, setup_directories, setup_logging

logger = setup_logging("Evaluation")


def _get_proba(model, X):
    """Obtain probability estimates; calibrate LinearSVC if needed."""
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)
    if isinstance(model, LinearSVC):
        calibrated = CalibratedClassifierCV(model, cv="prefit")
        # Refit calibration on same data is not ideal; use decision_function fallback
        scores = model.decision_function(X)
        if scores.ndim == 1:
            scores = np.column_stack([-scores, scores])
        exp_scores = np.exp(scores - scores.max(axis=1, keepdims=True))
        return exp_scores / exp_scores.sum(axis=1, keepdims=True)
    raise AttributeError("Model does not support probability estimates.")


def compute_metrics(y_true, y_pred, average: str = "weighted") -> dict:
    """Calculate standard classification metrics."""
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, average=average, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, average=average, zero_division=0)),
        "f1_weighted": float(f1_score(y_true, y_pred, average=average, zero_division=0)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
    }


def plot_confusion_matrix(
    y_true, y_pred, class_names: list[str], model_name: str
) -> None:
    """Generate and save confusion matrix heatmap."""
    configure_plot_style()
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names,
        ax=ax,
    )
    ax.set_title(f"Confusion Matrix — {model_name.replace('_', ' ').title()}")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    plt.tight_layout()
    path = FIGURES_DIR / f"confusion_matrix_{model_name}.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved: %s", path)


def plot_roc_curves(
    model, X_test, y_test, class_names: list[str], model_name: str
) -> None:
    """One-vs-rest ROC curves for multiclass classification."""
    configure_plot_style()
    n_classes = len(class_names)
    y_bin = label_binarize(y_test, classes=list(range(n_classes)))

    try:
        y_score = _get_proba(model, X_test)
    except AttributeError:
        logger.warning("Skipping ROC for %s (no probability support).", model_name)
        return

    fig, ax = plt.subplots(figsize=(10, 8))
    for i, class_name in enumerate(class_names):
        if y_bin[:, i].sum() == 0:
            continue
        fpr, tpr, _ = roc_curve(y_bin[:, i], y_score[:, i])
        auc = roc_auc_score(y_bin[:, i], y_score[:, i])
        ax.plot(fpr, tpr, label=f"{class_name} (AUC={auc:.3f})")

    ax.plot([0, 1], [0, 1], "k--", label="Random")
    ax.set_title(f"ROC Curves (OvR) — {model_name.replace('_', ' ').title()}")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.legend(loc="lower right", fontsize=9)
    plt.tight_layout()
    path = FIGURES_DIR / f"roc_curve_{model_name}.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved: %s", path)


def plot_model_comparison(results: dict) -> None:
    """Bar chart comparing metrics across all models."""
    configure_plot_style()
    metrics_df = pd.DataFrame(
        {
            name: {
                "Accuracy": res["accuracy"],
                "Precision": res["precision"],
                "Recall": res["recall"],
                "F1 Score": res["f1_weighted"],
            }
            for name, res in results.items()
        }
    ).T
    metrics_df.index = [n.replace("_", " ").title() for n in metrics_df.index]

    fig, ax = plt.subplots(figsize=(12, 6))
    metrics_df.plot(kind="bar", ax=ax, rot=15)
    ax.set_title("Model Performance Comparison")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="lower right")
    plt.tight_layout()
    path = FIGURES_DIR / "model_comparison.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved: %s", path)


def evaluate_model(model, X_test, y_test, model_name: str, class_names: list[str]) -> dict:
    """Full evaluation for a single model."""
    y_pred = model.predict(X_test)
    metrics = compute_metrics(y_test, y_pred)
    metrics["classification_report"] = classification_report(
        y_test, y_pred, target_names=class_names, zero_division=0
    )
    metrics["confusion_matrix"] = confusion_matrix(y_test, y_pred).tolist()
    metrics["model"] = model
    metrics["predictions"] = y_pred

    plot_confusion_matrix(y_test, y_pred, class_names, model_name)
    plot_roc_curves(model, X_test, y_test, class_names, model_name)
    return metrics


def evaluate_all_models(X_test, y_test, class_names: list[str]) -> dict:
    """Evaluate all saved models and persist comparison report."""
    setup_directories()
    results = {}

    for name in MODEL_CONFIGS:
        model_path = MODELS_DIR / f"{name}_model.joblib"
        if not model_path.exists():
            logger.warning("Model not found: %s. Skipping.", model_path)
            continue
        model = load_artifact(model_path)
        results[name] = evaluate_model(model, X_test, y_test, name, class_names)

    plot_model_comparison(results)

    # Save metrics JSON (exclude non-serializable objects)
    serializable = {}
    for name, res in results.items():
        serializable[name] = {
            k: v for k, v in res.items()
            if k not in ("model", "predictions")
        }

    metrics_path = METRICS_DIR / "evaluation_results.json"
    metrics_path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")

    report_path = METRICS_DIR / "classification_reports.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        for name, res in results.items():
            f.write(f"\n{'=' * 50}\n{name.upper()}\n{'=' * 50}\n")
            f.write(res["classification_report"])
            f.write("\n")

    logger.info("Evaluation complete. Results saved to outputs/metrics/")
    return results


if __name__ == "__main__":
    from src.data_cleaning import prepare_datasets

    data = prepare_datasets()
    evaluate_all_models(
        data["X_test"],
        data["y_test"],
        list(data["label_encoder"].classes_),
    )
