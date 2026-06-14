"""
Utility functions shared across the IDS pipeline.
"""

import logging
import sys
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from config.config import (
    DATA_PROCESSED_DIR,
    DATA_RAW_DIR,
    FIGURES_DIR,
    METRICS_DIR,
    MODELS_DIR,
    REPORTS_DIR,
)


def setup_directories() -> None:
    """Create all required project directories if they do not exist."""
    for directory in [
        DATA_RAW_DIR,
        DATA_PROCESSED_DIR,
        MODELS_DIR,
        FIGURES_DIR,
        METRICS_DIR,
        REPORTS_DIR,
    ]:
        directory.mkdir(parents=True, exist_ok=True)


def setup_logging(name: str = "IDS", level: int = logging.INFO) -> logging.Logger:
    """Configure and return a module logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger


def save_artifact(obj: object, path: Path) -> None:
    """Persist a Python object using joblib."""
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(obj, path)


def load_artifact(path: Path) -> object:
    """Load a persisted joblib artifact."""
    if not path.exists():
        raise FileNotFoundError(f"Artifact not found: {path}")
    return joblib.load(path)


def configure_plot_style() -> None:
    """Set consistent matplotlib/seaborn styling for all visualizations."""
    sns.set_theme(style="whitegrid", palette="husl")
    plt.rcParams.update(
        {
            "figure.figsize": (10, 6),
            "figure.dpi": 120,
            "font.size": 11,
            "axes.titlesize": 14,
            "axes.labelsize": 12,
        }
    )


def get_project_root() -> Path:
    """Return absolute path to project root."""
    return Path(__file__).resolve().parent.parent
