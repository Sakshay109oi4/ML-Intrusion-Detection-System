"""
Main pipeline orchestrator for ML-based Intrusion Detection System.
Run full pipeline or individual phases from command line.

Usage:
    python main.py --phase all
    python main.py --phase collect
    python main.py --phase clean
    python main.py --phase eda
    python main.py --phase train
    python main.py --phase evaluate
    python main.py --phase predict
    python main.py --gui
"""

import argparse
import sys
from pathlib import Path

# Ensure project root is on Python path (Windows-friendly)
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_collection import collect_dataset
from src.data_cleaning import prepare_datasets
from src.eda import run_eda
from src.model_training import train_all_models, select_best_model
from src.evaluation import evaluate_all_models
from src.prediction import get_default_feature_template, predict, format_prediction_result
from src.utils import setup_directories, setup_logging

logger = setup_logging("Main")


def run_collect(force: bool = False) -> None:
    """Phase 1: Dataset collection."""
    logger.info("=== Phase 1: Dataset Collection ===")
    collect_dataset(force=force)


def run_clean() -> dict:
    """Phase 2: Data cleaning and preprocessing."""
    logger.info("=== Phase 2: Data Cleaning ===")
    return prepare_datasets()


def run_eda_phase() -> None:
    """Phase 3: Exploratory data analysis."""
    logger.info("=== Phase 3: Exploratory Data Analysis ===")
    run_eda()


def run_train(data: dict | None = None) -> dict:
    """Phase 4: Model training."""
    logger.info("=== Phase 4: Model Training ===")
    if data is None:
        data = prepare_datasets()
    return train_all_models(data["X_train"], data["y_train"])


def run_evaluate(data: dict | None = None) -> dict:
    """Phase 5: Model evaluation."""
    logger.info("=== Phase 5: Model Evaluation ===")
    if data is None:
        data = prepare_datasets()
    results = evaluate_all_models(
        data["X_test"],
        data["y_test"],
        list(data["label_encoder"].classes_),
    )
    select_best_model(results)
    return results


def run_demo_predict() -> None:
    """Demo prediction with sample DoS-like features."""
    logger.info("=== Demo Prediction ===")
    sample = get_default_feature_template()
    sample.update({
        "duration": 0,
        "protocol_type": "tcp",
        "service": "http",
        "flag": "S0",
        "src_bytes": 0,
        "dst_bytes": 0,
        "serror_rate": 1.0,
        "srv_serror_rate": 1.0,
        "count": 511,
        "srv_count": 511,
    })
    result = predict(sample)
    print("\n" + format_prediction_result(result))


def run_full_pipeline(force_download: bool = False) -> None:
    """Execute all phases sequentially."""
    setup_directories()
    run_collect(force=force_download)
    data = run_clean()
    run_eda_phase()
    run_train(data)
    results = run_evaluate(data)

    logger.info("=== Pipeline Complete ===")
    for name, res in results.items():
        logger.info(
            "%s | Acc: %.4f | F1: %.4f",
            name,
            res["accuracy"],
            res["f1_weighted"],
        )


def launch_gui() -> None:
    """Launch real-time detection GUI."""
    from interface.gui_app import main as gui_main
    gui_main()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Machine Learning Based Intrusion Detection System (NSL-KDD)"
    )
    parser.add_argument(
        "--phase",
        choices=["all", "collect", "clean", "eda", "train", "evaluate", "predict"],
        default="all",
        help="Pipeline phase to run (default: all)",
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Re-download dataset even if files exist",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch real-time detection GUI",
    )
    args = parser.parse_args()

    if args.gui:
        launch_gui()
        return

    phase_map = {
        "all": lambda: run_full_pipeline(args.force_download),
        "collect": lambda: run_collect(args.force_download),
        "clean": run_clean,
        "eda": run_eda_phase,
        "train": run_train,
        "evaluate": run_evaluate,
        "predict": run_demo_predict,
    }
    phase_map[args.phase]()


if __name__ == "__main__":
    main()
