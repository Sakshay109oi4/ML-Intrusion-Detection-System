"""
Phase 3: Exploratory Data Analysis (EDA)
Traffic distribution, attack analysis, correlation, and feature importance.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier

from config.config import FIGURES_DIR, PROCESSED_TRAIN_PATH, RANDOM_STATE
from src.utils import configure_plot_style, setup_directories, setup_logging

logger = setup_logging("EDA")


def load_processed_train() -> pd.DataFrame:
    """Load cleaned training data for EDA."""
    if not PROCESSED_TRAIN_PATH.exists():
        raise FileNotFoundError(
            "Processed train data not found. Run data_cleaning.py first."
        )
    return pd.read_csv(PROCESSED_TRAIN_PATH)


def plot_traffic_distribution(df: pd.DataFrame) -> None:
    """Bar chart of normal vs attack traffic counts."""
    configure_plot_style()
    traffic = df["attack_category"].apply(
        lambda x: "Attack" if x != "Normal Traffic" else "Normal"
    )
    counts = traffic.value_counts()

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=counts.index, y=counts.values, ax=ax, palette="Set2")
    ax.set_title("Network Traffic Distribution (Normal vs Attack)")
    ax.set_xlabel("Traffic Type")
    ax.set_ylabel("Count")
    for i, v in enumerate(counts.values):
        ax.text(i, v + max(counts.values) * 0.01, str(v), ha="center")
    plt.tight_layout()
    path = FIGURES_DIR / "traffic_distribution.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved: %s", path)


def plot_attack_distribution(df: pd.DataFrame) -> None:
    """Distribution of five attack categories."""
    configure_plot_style()
    counts = df["attack_category"].value_counts()

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = sns.color_palette("husl", len(counts))
    ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", colors=colors)
    ax.set_title("Attack Category Distribution (NSL-KDD)")
    plt.tight_layout()
    path = FIGURES_DIR / "attack_distribution.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)

    # Bar chart variant
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=counts.index, y=counts.values, ax=ax, palette="viridis")
    ax.set_title("Attack Category Counts")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=25, ha="right")
    plt.tight_layout()
    path2 = FIGURES_DIR / "attack_distribution_bar.png"
    fig.savefig(path2, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved attack distribution plots.")


def plot_correlation_matrix(df: pd.DataFrame) -> None:
    """Heatmap of numeric feature correlations."""
    configure_plot_style()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) < 2:
        logger.warning("Insufficient numeric columns for correlation.")
        return

    corr = df[numeric_cols].corr()
    fig, ax = plt.subplots(figsize=(14, 12))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(
        corr,
        mask=mask,
        cmap="coolwarm",
        center=0,
        ax=ax,
        square=True,
        linewidths=0.3,
        cbar_kws={"shrink": 0.8},
    )
    ax.set_title("Feature Correlation Matrix (Numeric Features)")
    plt.tight_layout()
    path = FIGURES_DIR / "correlation_matrix.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved: %s", path)


def plot_feature_importance(df: pd.DataFrame, top_n: int = 20) -> None:
    """
    Train a quick Random Forest on raw features to estimate importance.
    Uses label-encoded target for speed during EDA.
    """
    configure_plot_style()
    from sklearn.preprocessing import LabelEncoder, OneHotEncoder
    from config.config import CATEGORICAL_COLUMNS

    feature_cols = [c for c in df.columns if c != "attack_category"]
    X = df[feature_cols].copy()
    y = LabelEncoder().fit_transform(df["attack_category"])

    # Simple encoding for EDA importance
    for col in CATEGORICAL_COLUMNS:
        if col in X.columns:
            dummies = pd.get_dummies(X[col], prefix=col)
            X = pd.concat([X.drop(columns=[col]), dummies], axis=1)

    rf = RandomForestClassifier(
        n_estimators=50, max_depth=12, random_state=RANDOM_STATE, n_jobs=-1
    )
    rf.fit(X, y)

    importance = pd.Series(rf.feature_importances_, index=X.columns)
    top_features = importance.nlargest(top_n)

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(x=top_features.values, y=top_features.index, ax=ax, palette="mako")
    ax.set_title(f"Top {top_n} Feature Importances (Random Forest EDA)")
    ax.set_xlabel("Importance Score")
    plt.tight_layout()
    path = FIGURES_DIR / "feature_importance.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved: %s", path)


def generate_eda_report(df: pd.DataFrame) -> str:
    """Create a text summary of EDA findings."""
    lines = [
        "=" * 60,
        "EXPLORATORY DATA ANALYSIS REPORT",
        "=" * 60,
        f"Total Records: {len(df)}",
        f"Features: {len(df.columns) - 1}",
        "",
        "Attack Category Distribution:",
    ]
    for cat, count in df["attack_category"].value_counts().items():
        pct = 100 * count / len(df)
        lines.append(f"  {cat}: {count} ({pct:.2f}%)")

    lines.extend(["", "Basic Statistics (Numeric):", df.describe().to_string()])
    report = "\n".join(lines)

    report_path = FIGURES_DIR.parent / "reports" / "eda_summary.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    logger.info("EDA report saved to %s", report_path)
    return report


def run_eda(data: pd.DataFrame | None = None) -> None:
    """Execute full EDA pipeline."""
    setup_directories()
    df = data if data is not None else load_processed_train()

    plot_traffic_distribution(df)
    plot_attack_distribution(df)
    plot_correlation_matrix(df)
    plot_feature_importance(df)
    generate_eda_report(df)
    logger.info("EDA complete. Figures saved to outputs/figures/")


if __name__ == "__main__":
    run_eda()
