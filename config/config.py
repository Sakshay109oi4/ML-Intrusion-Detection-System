"""
Central configuration for the ML-based Intrusion Detection System (IDS).
All paths are resolved relative to the project root for Windows portability.
"""

from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Data paths
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TRAIN_FILENAME = "KDDTrain+.txt"
TEST_FILENAME = "KDDTest+.txt"
TRAIN_PATH = DATA_RAW_DIR / TRAIN_FILENAME
TEST_PATH = DATA_RAW_DIR / TEST_FILENAME
PROCESSED_TRAIN_PATH = DATA_PROCESSED_DIR / "train_processed.csv"
PROCESSED_TEST_PATH = DATA_PROCESSED_DIR / "test_processed.csv"

# Model and artifact paths
MODELS_DIR = PROJECT_ROOT / "models"
BEST_MODEL_PATH = MODELS_DIR / "best_ids_model.joblib"
PREPROCESSOR_PATH = MODELS_DIR / "preprocessor.joblib"
LABEL_ENCODER_PATH = MODELS_DIR / "label_encoder.joblib"
FEATURE_NAMES_PATH = MODELS_DIR / "feature_names.joblib"

# Output paths
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
METRICS_DIR = OUTPUTS_DIR / "metrics"
REPORTS_DIR = OUTPUTS_DIR / "reports"

# NSL-KDD dataset column names (41 features + label + difficulty on test)
COLUMN_NAMES = [
    "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes",
    "land", "wrong_fragment", "urgent", "hot", "num_failed_logins", "logged_in",
    "num_compromised", "root_shell", "su_attempted", "num_root", "num_file_creations",
    "num_shells", "num_access_files", "num_outbound_cmds", "is_host_login",
    "is_guest_login", "count", "srv_count", "serror_rate", "srv_serror_rate",
    "rerror_rate", "srv_rerror_rate", "same_srv_rate", "diff_srv_rate",
    "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count",
    "dst_host_same_srv_rate", "dst_host_diff_srv_rate", "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate", "dst_host_serror_rate", "dst_host_srv_serror_rate",
    "dst_host_rerror_rate", "dst_host_srv_rerror_rate", "label", "difficulty",
]

# Categorical columns requiring encoding
CATEGORICAL_COLUMNS = ["protocol_type", "service", "flag"]

# Attack category mapping (NSL-KDD specific attack names -> 5 classes)
ATTACK_MAPPING = {
    "normal": "Normal Traffic",
    "back": "DoS Attack",
    "land": "DoS Attack",
    "neptune": "DoS Attack",
    "pod": "DoS Attack",
    "smurf": "DoS Attack",
    "teardrop": "DoS Attack",
    "mailbomb": "DoS Attack",
    "apache2": "DoS Attack",
    "processtable": "DoS Attack",
    "udpstorm": "DoS Attack",
    "ipsweep": "Probe Attack",
    "mscan": "Probe Attack",
    "nmap": "Probe Attack",
    "portsweep": "Probe Attack",
    "saint": "Probe Attack",
    "satan": "Probe Attack",
    "ftp_write": "R2L Attack",
    "guess_passwd": "R2L Attack",
    "httptunnel": "R2L Attack",
    "imap": "R2L Attack",
    "multihop": "R2L Attack",
    "named": "R2L Attack",
    "phf": "R2L Attack",
    "sendmail": "R2L Attack",
    "snmpgetattack": "R2L Attack",
    "snmpguess": "R2L Attack",
    "spy": "R2L Attack",
    "warezclient": "R2L Attack",
    "warezmaster": "R2L Attack",
    "xlock": "R2L Attack",
    "xsnoop": "R2L Attack",
    "buffer_overflow": "U2R Attack",
    "loadmodule": "U2R Attack",
    "perl": "U2R Attack",
    "rootkit": "U2R Attack",
    "ps": "U2R Attack",
    "sqlattack": "U2R Attack",
    "xterm": "U2R Attack",
}

TARGET_CLASSES = [
    "Normal Traffic",
    "DoS Attack",
    "Probe Attack",
    "R2L Attack",
    "U2R Attack",
]

# Model hyperparameters
RANDOM_STATE = 42
TEST_SIZE = 0.2
N_JOBS = -1

MODEL_CONFIGS = {
    "random_forest": {
        "classifier": "RandomForestClassifier",
        "params": {
            "n_estimators": 100,
            "max_depth": 20,
            "min_samples_split": 5,
            "min_samples_leaf": 2,
            "random_state": RANDOM_STATE,
            "n_jobs": N_JOBS,
        },
    },
    "decision_tree": {
        "classifier": "DecisionTreeClassifier",
        "params": {
            "max_depth": 15,
            "min_samples_split": 10,
            "min_samples_leaf": 5,
            "random_state": RANDOM_STATE,
        },
    },
    "logistic_regression": {
        "classifier": "LogisticRegression",
        "params": {
            "max_iter": 1000,
            "solver": "lbfgs",
            "random_state": RANDOM_STATE,
        },
    },
    "svm": {
        "classifier": "LinearSVC",
        "params": {
            "C": 1.0,
            "max_iter": 2000,
            "random_state": RANDOM_STATE,
            "dual": "auto",
        },
    },
}

# NSL-KDD download URLs (public mirrors)
DATASET_URLS = {
    TRAIN_FILENAME: "https://raw.githubusercontent.com/DefCode/NSL-KDD/master/KDDTrain%2B.txt",
    TEST_FILENAME: "https://raw.githubusercontent.com/DefCode/NSL-KDD/master/KDDTest%2B.txt",
}

# Fallback mirror
DATASET_URLS_FALLBACK = {
    TRAIN_FILENAME: "https://raw.githubusercontent.com/shavak/NSL-KDD/master/KDDTrain%2B.txt",
    TEST_FILENAME: "https://raw.githubusercontent.com/shavak/NSL-KDD/master/KDDTest%2B.txt",
}
