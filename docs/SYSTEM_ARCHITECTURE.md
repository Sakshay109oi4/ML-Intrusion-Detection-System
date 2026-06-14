# System Architecture & Diagrams
## Machine Learning Based Intrusion Detection System

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INTRUSION DETECTION SYSTEM (IDS)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐  │
│  │   DATA       │    │  PREPROCESS  │    │   ML MODEL   │    │  DETECTION │  │
│  │   LAYER      │───▶│   ENGINE     │───▶│   LAYER      │───▶│  INTERFACE │  │
│  └──────────────┘    └──────────────┘    └──────────────┘    └────────────┘  │
│         │                   │                   │                   │        │
│  NSL-KDD Dataset      Cleaning &           RF / DT / LR /      Tkinter GUI   │
│  KDDTrain+.txt        Encoding &           SVM Classifiers     CLI Predict   │
│  KDDTest+.txt         Scaling                                              │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                         SUPPORTING COMPONENTS                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │
│  │ Config      │  │ EDA Module  │  │ Evaluation  │  │ Model Storage   │   │
│  │ (config.py) │  │ (eda.py)    │  │ (eval.py)   │  │ (joblib .pkl)   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Flow Diagram

```mermaid
flowchart LR
    A[NSL-KDD Raw Data] --> B[Data Collection]
    B --> C[Data Cleaning]
    C --> D{Missing Values?}
    D -->|Yes| E[Drop / Impute]
    D -->|No| F[Duplicate Removal]
    E --> F
    F --> G[Label Mapping]
    G --> H[Feature Encoding]
    H --> I[Feature Scaling]
    I --> J[Train/Test Split]
    J --> K[Model Training]
    K --> L[Model Evaluation]
    L --> M[Best Model Selection]
    M --> N[Saved Model]
    N --> O[Real-Time Prediction]
    O --> P[Normal / DoS / Probe / R2L / U2R]
```

### Detailed Data Flow

```
INPUT: KDDTrain+.txt, KDDTest+.txt (41 features + label)
   │
   ▼
[Phase 1] Download / Load Raw CSV
   │
   ▼
[Phase 2] Clean → Encode → Scale
   │  • Remove duplicates (~77K removed from original KDD)
   │  • Map 40+ attack names → 5 categories
   │  • OneHotEncode: protocol_type, service, flag
   │  • StandardScaler: 38 numeric features
   ▼
[Phase 3] EDA → Visualizations saved to outputs/figures/
   │
   ▼
[Phase 4] Train 4 classifiers on X_train (125,973 samples)
   │
   ▼
[Phase 5] Evaluate on X_test (22,544 samples)
   │  • Accuracy, Precision, Recall, F1
   │  • Confusion Matrix, ROC-AUC
   ▼
[Phase 6] Deploy best model → GUI / API prediction
   │
   ▼
OUTPUT: Attack classification + confidence score
```

---

## 3. Workflow Diagram

```mermaid
flowchart TD
    Start([Start]) --> Setup[Setup Environment & Install Dependencies]
    Setup --> Collect[Phase 1: Collect NSL-KDD Dataset]
    Collect --> Clean[Phase 2: Data Cleaning & Preprocessing]
    Clean --> EDA[Phase 3: Exploratory Data Analysis]
    EDA --> Train[Phase 4: Train ML Models]
    Train --> RF[Random Forest]
    Train --> DT[Decision Tree]
    Train --> LR[Logistic Regression]
    Train --> SVM[SVM]
    RF --> Eval[Phase 5: Evaluate All Models]
    DT --> Eval
    LR --> Eval
    SVM --> Eval
    Eval --> Compare[Compare Metrics]
    Compare --> Best[Select Best Model]
    Best --> Save[Save Model & Preprocessor]
    Save --> GUI[Phase 6: Real-Time GUI]
    GUI --> Input[User Inputs Network Features]
    Input --> Predict[Model Predicts Attack Type]
    Predict --> Display[Display Result + Confidence]
    Display --> End([End])
```

---

## 4. UML Diagrams

### 4.1 Use Case Diagram

```mermaid
flowchart TB
    subgraph Actors
        User((Security Analyst))
        Admin((System Admin))
    end

    subgraph IDS_System["Intrusion Detection System"]
        UC1[Download Dataset]
        UC2[Preprocess Data]
        UC3[Train Models]
        UC4[Evaluate Models]
        UC5[View EDA Reports]
        UC6[Real-Time Detection]
        UC7[Load Sample Traffic]
    end

    Admin --> UC1
    Admin --> UC2
    Admin --> UC3
    Admin --> UC4
    Admin --> UC5
    User --> UC6
    User --> UC7
    User --> UC5
```

### 4.2 Class Diagram

```mermaid
classDiagram
    class DataCollection {
        +collect_dataset(force: bool) tuple
        -download_file(url, dest) bool
    }

    class DataCleaning {
        +load_raw_data() tuple
        +clean_dataframe(df) DataFrame
        +build_preprocessor() ColumnTransformer
        +prepare_datasets() dict
    }

    class EDA {
        +run_eda(data) void
        +plot_traffic_distribution(df) void
        +plot_attack_distribution(df) void
        +plot_correlation_matrix(df) void
        +plot_feature_importance(df) void
    }

    class ModelTraining {
        +train_all_models(X, y) dict
        +select_best_model(results) tuple
        -get_classifier(name) Classifier
    }

    class Evaluation {
        +evaluate_all_models(X, y, classes) dict
        +compute_metrics(y_true, y_pred) dict
        +plot_confusion_matrix() void
        +plot_roc_curves() void
    }

    class Prediction {
        +predict(features) dict
        +load_prediction_artifacts() tuple
        +validate_input(features) DataFrame
    }

    class IntrusionDetectionApp {
        -entries: dict
        +_on_predict() void
        +_load_normal() void
        +_load_dos() void
    }

    DataCollection --> DataCleaning : provides raw data
    DataCleaning --> EDA : provides processed data
    DataCleaning --> ModelTraining : provides X, y
    ModelTraining --> Evaluation : provides models
    Evaluation --> Prediction : selects best model
    Prediction --> IntrusionDetectionApp : used by GUI
```

### 4.3 Sequence Diagram — Real-Time Prediction

```mermaid
sequenceDiagram
    actor User
    participant GUI as Tkinter GUI
    participant Pred as prediction.py
    participant Prep as preprocessor.joblib
    participant Model as best_ids_model.joblib
    participant LE as label_encoder.joblib

    User->>GUI: Enter network features
    User->>GUI: Click "Detect Intrusion"
    GUI->>Pred: predict(features_dict)
    Pred->>Pred: validate_input()
    Pred->>Prep: transform(features)
    Prep-->>Pred: X_scaled_encoded
    Pred->>Model: predict(X)
    Model-->>Pred: class_index
    Pred->>Model: predict_proba(X)
    Model-->>Pred: probabilities
    Pred->>LE: inverse_transform(class_index)
    LE-->>Pred: "DoS Attack"
    Pred-->>GUI: {prediction, confidence, probabilities}
    GUI-->>User: Display colored result
```

### 4.4 Component Diagram

```mermaid
flowchart TB
    subgraph Presentation
        GUI[gui_app.py]
        CLI[main.py CLI]
    end

    subgraph Application
        Pred[prediction.py]
        Train[model_training.py]
        Eval[evaluation.py]
    end

    subgraph DataProcessing
        Collect[data_collection.py]
        Clean[data_cleaning.py]
        EDAmod[eda.py]
    end

    subgraph Infrastructure
        Config[config.py]
        Utils[utils.py]
    end

    subgraph Storage
        RawData[(data/raw/)]
        Models[(models/)]
        Outputs[(outputs/)]
    end

    GUI --> Pred
    CLI --> Collect
    CLI --> Clean
    CLI --> EDAmod
    CLI --> Train
    CLI --> Eval
    Pred --> Models
    Train --> Models
    Eval --> Outputs
    Collect --> RawData
    Clean --> RawData
    Clean --> Models
    EDAmod --> Outputs
    Config --> Collect
    Config --> Clean
    Config --> Train
    Utils --> EDAmod
    Utils --> Eval
```

---

## 5. Deployment Architecture

```
┌─────────────────────────────────────────────────┐
│              DEVELOPMENT / DEMO                  │
│  ┌─────────┐  ┌─────────┐  ┌─────────────────┐ │
│  │ Python  │  │ Joblib  │  │ Tkinter GUI     │ │
│  │ 3.9+    │  │ Models  │  │ (Local Desktop) │ │
│  └─────────┘  └─────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────┘
                        │
                        ▼ (Future Production)
┌─────────────────────────────────────────────────┐
│              PRODUCTION (Future Scope)             │
│  ┌─────────┐  ┌─────────┐  ┌─────────────────┐ │
│  │ Packet  │  │ FastAPI │  │ Web Dashboard   │ │
│  │ Capture │→ │ REST API│→ │ (React/Streamlit)│ │
│  └─────────┘  └─────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────┘
```

---

## 6. Security Considerations

| Layer | Consideration |
|-------|---------------|
| Data | NSL-KDD is public benchmark data; no PII |
| Model | Serialized with joblib; validate inputs before inference |
| GUI | Local-only; no network exposure |
| Production | Would require HTTPS, authentication, rate limiting |

---

*Document Version: 1.0 | Project: ML-Based IDS | Dataset: NSL-KDD*
