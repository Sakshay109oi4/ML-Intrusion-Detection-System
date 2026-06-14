"""
Phase 2: Data Cleaning
Handles missing values, duplicates, feature encoding, and scaling.
"""

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

from config.config import (
    ATTACK_MAPPING,
    CATEGORICAL_COLUMNS,
    COLUMN_NAMES,
    FEATURE_NAMES_PATH,
    LABEL_ENCODER_PATH,
    PREPROCESSOR_PATH,
    PROCESSED_TEST_PATH,
    PROCESSED_TRAIN_PATH,
    RANDOM_STATE,
    TEST_PATH,
    TRAIN_PATH,
)
from src.utils import save_artifact, setup_logging

logger = setup_logging("DataCleaning")


def load_raw_data(train_path=None, test_path=None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load raw NSL-KDD CSV files into DataFrames."""
    train_path = train_path or TRAIN_PATH
    test_path = test_path or TEST_PATH

    train_df = pd.read_csv(train_path, names=COLUMN_NAMES, header=None)
    test_df = pd.read_csv(test_path, names=COLUMN_NAMES, header=None)

    logger.info("Loaded train: %s rows, test: %s rows", len(train_df), len(test_df))
    return train_df, test_df


def map_attack_labels(label: str) -> str:
    """Map raw attack name to one of five traffic categories."""
    normalized = str(label).strip().lower().replace(".", "")
    return ATTACK_MAPPING.get(normalized, "R2L Attack")


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply cleaning steps: handle missing values, remove duplicates,
    normalize labels, and drop difficulty column.
    """
    df = df.copy()

    # Replace invalid placeholders with NaN
    df.replace(["?", " ", ""], pd.NA, inplace=True)

    missing_before = df.isnull().sum().sum()
    if missing_before > 0:
        logger.info("Missing values found: %d. Dropping affected rows.", missing_before)
        df.dropna(inplace=True)

    duplicates = df.duplicated().sum()
    if duplicates > 0:
        logger.info("Removing %d duplicate rows.", duplicates)
        df.drop_duplicates(inplace=True)

    # Map granular attack labels to 5-class taxonomy
    df["attack_category"] = df["label"].apply(map_attack_labels)

    # Drop original label and difficulty (not a predictive feature)
    df.drop(columns=["label", "difficulty"], inplace=True, errors="ignore")

    df.reset_index(drop=True, inplace=True)
    return df


def build_preprocessor() -> ColumnTransformer:
    """Create sklearn preprocessing pipeline for numeric and categorical features."""
    numeric_features = [
        col for col in COLUMN_NAMES
        if col not in CATEGORICAL_COLUMNS + ["label", "difficulty"]
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_COLUMNS,
            ),
        ],
        remainder="drop",
    )
    return preprocessor


def get_feature_names(preprocessor: ColumnTransformer) -> list[str]:
    """Extract human-readable feature names after transformation."""
    return list(preprocessor.get_feature_names_out())


def prepare_datasets(
    save_processed: bool = True,
) -> dict:
    """
    Full cleaning pipeline: load, clean, encode, scale, and split.

    Returns
    -------
    dict
        Contains X_train, X_test, y_train, y_test, preprocessor, label_encoder.
    """
    train_df, test_df = load_raw_data()
    train_clean = clean_dataframe(train_df)
    test_clean = clean_dataframe(test_df)

    if save_processed:
        train_clean.to_csv(PROCESSED_TRAIN_PATH, index=False)
        test_clean.to_csv(PROCESSED_TEST_PATH, index=False)
        logger.info("Saved processed CSVs to data/processed/")

    feature_columns = [c for c in train_clean.columns if c != "attack_category"]
    X_train_raw = train_clean[feature_columns]
    y_train_raw = train_clean["attack_category"]
    X_test_raw = test_clean[feature_columns]
    y_test_raw = test_clean["attack_category"]

    label_encoder = LabelEncoder()
    label_encoder.fit(list(y_train_raw) + list(y_test_raw))
    y_train = label_encoder.transform(y_train_raw)
    y_test = label_encoder.transform(y_test_raw)

    preprocessor = build_preprocessor()
    X_train = preprocessor.fit_transform(X_train_raw)
    X_test = preprocessor.transform(X_test_raw)

    feature_names = get_feature_names(preprocessor)

    save_artifact(preprocessor, PREPROCESSOR_PATH)
    save_artifact(label_encoder, LABEL_ENCODER_PATH)
    save_artifact(feature_names, FEATURE_NAMES_PATH)

    logger.info(
        "Preprocessing complete. Features: %d | Classes: %s",
        X_train.shape[1],
        list(label_encoder.classes_),
    )

    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "X_train_raw": X_train_raw,
        "X_test_raw": X_test_raw,
        "y_train_raw": y_train_raw,
        "y_test_raw": y_test_raw,
        "preprocessor": preprocessor,
        "label_encoder": label_encoder,
        "feature_names": feature_names,
    }


def prepare_validation_split(X, y, test_size: float = 0.2):
    """Optional stratified validation split from training data."""
    return train_test_split(
        X, y, test_size=test_size, random_state=RANDOM_STATE, stratify=y
    )


if __name__ == "__main__":
    prepare_datasets()
