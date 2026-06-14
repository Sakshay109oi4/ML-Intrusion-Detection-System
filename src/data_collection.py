"""
Phase 1: Dataset Collection
Downloads NSL-KDD train and test datasets from public mirrors.
"""

import urllib.error
import urllib.request
from pathlib import Path

from config.config import (
    DATA_RAW_DIR,
    DATASET_URLS,
    DATASET_URLS_FALLBACK,
    TEST_FILENAME,
    TRAIN_FILENAME,
)
from src.utils import setup_directories, setup_logging

logger = setup_logging("DataCollection")


def download_file(url: str, destination: Path) -> bool:
    """
    Download a file from URL to destination path.
    Returns True on success, False on failure.
    """
    try:
        logger.info("Downloading from %s ...", url)
        urllib.request.urlretrieve(url, destination)
        logger.info("Saved to %s", destination)
        return True
    except (urllib.error.URLError, OSError) as exc:
        logger.warning("Download failed: %s", exc)
        return False


def collect_dataset(force: bool = False) -> tuple[Path, Path]:
    """
    Collect NSL-KDD dataset files.

    Parameters
    ----------
    force : bool
        Re-download even if files already exist.

    Returns
    -------
    tuple[Path, Path]
        Paths to training and test files.
    """
    setup_directories()
    train_path = DATA_RAW_DIR / TRAIN_FILENAME
    test_path = DATA_RAW_DIR / TEST_FILENAME

    for filename, primary_url in DATASET_URLS.items():
        dest = DATA_RAW_DIR / filename
        if dest.exists() and not force:
            logger.info("%s already exists. Skipping download.", filename)
            continue

        success = download_file(primary_url, dest)
        if not success:
            fallback_url = DATASET_URLS_FALLBACK[filename]
            success = download_file(fallback_url, dest)

        if not success:
            raise RuntimeError(
                f"Could not download {filename}. "
                "Place KDDTrain+.txt and KDDTest+.txt manually in data/raw/."
            )

    if not train_path.exists() or not test_path.exists():
        raise FileNotFoundError(
            "Dataset files missing. Expected KDDTrain+.txt and KDDTest+.txt in data/raw/."
        )

    logger.info("Dataset collection complete.")
    return train_path, test_path


if __name__ == "__main__":
    collect_dataset()
