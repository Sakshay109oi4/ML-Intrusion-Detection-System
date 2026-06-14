# Machine Learning Based Intrusion Detection System

A complete, internship-ready **Intrusion Detection System (IDS)** that classifies network traffic into five categories using the **NSL-KDD** dataset and multiple machine learning algorithms.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.3+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## Overview

This project detects malicious network traffic and classifies attacks using supervised machine learning. It implements a full ML pipeline from data collection through real-time prediction.

### Attack Categories Detected

| Class | Description | Example Attacks |
|-------|-------------|-----------------|
| **Normal Traffic** | Legitimate connections | — |
| **DoS Attack** | Denial of Service | neptune, smurf, teardrop |
| **Probe Attack** | Network scanning | nmap, portsweep, satan |
| **R2L Attack** | Remote to Local | guess_passwd, ftp_write |
| **U2R Attack** | User to Root | buffer_overflow, rootkit |

### Models Compared

1. Random Forest Classifier
2. Decision Tree Classifier
3. Logistic Regression
4. Support Vector Machine (LinearSVC)

---

## Project Structure

```
ml-intrusion-detection-system/
├── main.py                      # Pipeline orchestrator & CLI entry point
├── requirements.txt             # Python dependencies
├── INSTALLATION.md              # Step-by-step setup guide
├── config/
│   └── config.py                # Paths, hyperparameters, attack mappings
├── src/
│   ├── data_collection.py       # Phase 1: Download NSL-KDD dataset
│   ├── data_cleaning.py         # Phase 2: Cleaning, encoding, scaling
│   ├── eda.py                   # Phase 3: Exploratory data analysis
│   ├── model_training.py        # Phase 4: Train 4 ML models
│   ├── evaluation.py            # Phase 5: Metrics & visualizations
│   ├── prediction.py            # Phase 6: Inference module
│   └── utils.py                 # Shared utilities
├── interface/
│   └── gui_app.py               # Real-time Tkinter detection GUI
├── data/
│   ├── raw/                     # NSL-KDD raw files
│   └── processed/               # Cleaned CSV outputs
├── models/                      # Saved models (.joblib)
├── outputs/
│   ├── figures/                 # EDA plots, confusion matrices, ROC
│   ├── metrics/                 # JSON evaluation results
│   └── reports/                 # Text reports
└── docs/
    ├── PROJECT_REPORT.md        # 20-page detailed project report
    ├── SYSTEM_ARCHITECTURE.md   # Architecture & diagrams
    ├── RESEARCH_METHODOLOGY.md  # Research approach
    ├── VIVA_QUESTIONS.md        # Interview Q&A
    └── LINKEDIN_DESCRIPTION.md  # LinkedIn project write-up
```

---

## Quick Start (Windows)

### 1. Prerequisites

- Python 3.9 or higher
- pip package manager
- Internet connection (for dataset download)

### 2. Installation

```powershell
# Clone or navigate to project directory
cd C:\Users\Sakshay\ml-intrusion-detection-system

# Create virtual environment (recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Full Pipeline

```powershell
python main.py --phase all
```

This executes all six phases:
1. Downloads NSL-KDD dataset
2. Cleans and preprocesses data
3. Generates EDA visualizations
4. Trains all four models
5. Evaluates and saves best model
6. Runs demo prediction

**Expected runtime:** 5–15 minutes (depends on hardware)

### 4. Launch Real-Time GUI

```powershell
python main.py --gui
```

Or directly:

```powershell
python interface/gui_app.py
```

---

## Individual Phase Commands

| Phase | Command | Output |
|-------|---------|--------|
| Collect | `python main.py --phase collect` | `data/raw/KDDTrain+.txt` |
| Clean | `python main.py --phase clean` | `data/processed/`, `models/preprocessor.joblib` |
| EDA | `python main.py --phase eda` | `outputs/figures/*.png` |
| Train | `python main.py --phase train` | `models/*_model.joblib` |
| Evaluate | `python main.py --phase evaluate` | `outputs/metrics/`, ROC curves |
| Predict | `python main.py --phase predict` | Console demo output |

---

## Sample Results

After running the pipeline, expect approximately:

| Model | Accuracy | F1 Score |
|-------|----------|----------|
| Random Forest | ~0.97+ | ~0.97+ |
| Decision Tree | ~0.96+ | ~0.96+ |
| Logistic Regression | ~0.90+ | ~0.90+ |
| SVM (Linear) | ~0.92+ | ~0.92+ |

> Actual values depend on hardware and sklearn version. See `outputs/metrics/evaluation_results.json`.

---

## Generated Outputs

### Visualizations (`outputs/figures/`)
- Traffic distribution (normal vs attack)
- Attack category distribution
- Correlation heatmap
- Feature importance chart
- Confusion matrices (per model)
- ROC curves (per model)
- Model comparison bar chart

### Saved Models (`models/`)
- `random_forest_model.joblib`
- `decision_tree_model.joblib`
- `logistic_regression_model.joblib`
- `svm_model.joblib`
- `best_ids_model.joblib`
- `preprocessor.joblib`
- `label_encoder.joblib`

---

## Using the Prediction Module

```python
from src.prediction import predict, get_default_feature_template

features = get_default_feature_template()
features["serror_rate"] = 1.0
features["flag"] = "S0"
features["count"] = 511

result = predict(features)
print(result["prediction"])   # e.g., "DoS Attack"
print(result["confidence"])   # e.g., 0.94
```

---

## Tech Stack

- **Python 3.9+**
- **Pandas** — Data manipulation
- **NumPy** — Numerical computing
- **Scikit-learn** — ML algorithms & preprocessing
- **Matplotlib & Seaborn** — Visualization
- **Joblib** — Model serialization
- **Tkinter** — GUI (built-in)

---

## Documentation

| Document | Description |
|----------|-------------|
| [INSTALLATION.md](INSTALLATION.md) | Detailed Windows setup |
| [docs/PROJECT_REPORT.md](docs/PROJECT_REPORT.md) | Full 20-page project report |
| [docs/SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md) | Architecture & diagrams |
| [docs/RESEARCH_METHODOLOGY.md](docs/RESEARCH_METHODOLOGY.md) | Research methodology |
| [docs/VIVA_QUESTIONS.md](docs/VIVA_QUESTIONS.md) | Viva preparation Q&A |
| [docs/LINKEDIN_DESCRIPTION.md](docs/LINKEDIN_DESCRIPTION.md) | LinkedIn project text |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Dataset download fails | Manually place `KDDTrain+.txt` and `KDDTest+.txt` in `data/raw/` |
| `ModuleNotFoundError: config` | Run commands from project root directory |
| GUI won't open | Ensure models exist: run `python main.py --phase all` first |
| Slow SVM training | Normal for large datasets; reduce samples in config if needed |

---

## Future Enhancements

- Deep learning models (CNN, LSTM) for sequence-based detection
- Real-time packet capture integration (Scapy/pyshark)
- Web dashboard (Flask/Streamlit)
- SMOTE for class imbalance handling
- SHAP explainability for predictions

---

## Author

Sakshay
