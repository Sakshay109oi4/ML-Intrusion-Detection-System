# Research Methodology
## Machine Learning Based Intrusion Detection System

---

## 1. Research Problem

Network intrusions pose significant threats to organizational security. Traditional signature-based intrusion detection systems fail against novel (zero-day) attacks. This research investigates whether **supervised machine learning** can effectively classify network connections into normal and attack categories using flow-level features from the NSL-KDD benchmark dataset.

### Research Questions

1. Can ML classifiers accurately distinguish normal traffic from four attack types (DoS, Probe, R2L, U2R)?
2. Which algorithm achieves the best balance of accuracy, precision, and recall?
3. Which network features contribute most to intrusion detection?

---

## 2. Research Design

| Aspect | Description |
|--------|-------------|
| **Type** | Experimental, quantitative |
| **Approach** | Supervised multi-class classification |
| **Dataset** | NSL-KDD (improved KDD Cup 99) |
| **Validation** | Hold-out test set (official NSL-KDD test split) |
| **Comparison** | Four algorithms under identical preprocessing |

---

## 3. Dataset Selection Rationale

### Why NSL-KDD?

The original KDD Cup 99 dataset suffered from:
- **Redundant records** — Biased classifiers toward frequent records
- **Duplicate bias** — Multiple copies of easy-to-detect attacks

NSL-KDD (Tavallaee et al., 2009) addresses these issues by:
- Removing redundant records
- Creating difficulty levels per record
- Providing a balanced, realistic benchmark

### Dataset Statistics

| Split | Records | Features | Classes |
|-------|---------|----------|---------|
| Training | 125,973 | 41 | 5 (mapped) |
| Testing | 22,544 | 41 | 5 (mapped) |

---

## 4. Methodology Steps

### Step 1: Data Collection
- Automated download from public GitHub mirrors
- Manual fallback for reproducibility

### Step 2: Data Preprocessing

```
Raw Label (e.g., "neptune.") 
    → Normalized ("neptune")
    → Category Mapped ("DoS Attack")
    → Label Encoded (integer 0-4)
```

**Encoding Strategy:**
- Categorical (protocol, service, flag): One-Hot Encoding
- Numeric (38 features): StandardScaler (zero mean, unit variance)

**Cleaning:**
- Missing value removal
- Duplicate elimination
- Difficulty column dropped (test metadata, not predictive)

### Step 3: Exploratory Data Analysis
- Class distribution analysis (identify imbalance)
- Correlation analysis (detect multicollinearity)
- Feature importance via Random Forest (inform feature selection)

### Step 4: Model Selection

| Algorithm | Rationale |
|-----------|-----------|
| **Random Forest** | Ensemble method; handles non-linearity; robust to noise |
| **Decision Tree** | Interpretable baseline; shows decision boundaries |
| **Logistic Regression** | Linear baseline; fast; probabilistic output |
| **SVM (Linear)** | Maximum-margin classifier; effective in high dimensions |

### Step 5: Hyperparameters

Selected via literature review and preliminary experiments (not exhaustive grid search to maintain internship scope):

- Random Forest: 100 trees, max_depth=20
- Decision Tree: max_depth=15, min_samples_leaf=5
- Logistic Regression: multinomial, LBFGS solver, max_iter=1000
- LinearSVC: C=1.0, max_iter=2000

### Step 6: Evaluation Metrics

| Metric | Formula / Purpose |
|--------|-------------------|
| **Accuracy** | Overall correct predictions |
| **Precision** | TP / (TP + FP) — minimize false alarms |
| **Recall** | TP / (TP + FN) — catch all attacks |
| **F1 Score** | Harmonic mean of precision and recall |
| **Confusion Matrix** | Per-class error analysis |
| **ROC-AUC** | One-vs-rest discrimination ability |

**Primary selection criterion:** Weighted F1 Score (accounts for class imbalance).

---

## 5. Experimental Setup

```
Environment:
  - Python 3.9+
  - scikit-learn 1.3+
  - Windows 10/11

Reproducibility:
  - random_state = 42 (all stochastic algorithms)
  - Fixed train/test split (official NSL-KDD partition)

Hardware:
  - CPU-based training (no GPU required)
  - n_jobs = -1 (parallel where supported)
```

---

## 6. Limitations

1. **Dataset age** — NSL-KDD reflects 1990s network traffic patterns
2. **Class imbalance** — U2R and R2L are underrepresented
3. **Flow-level features** — Not real-time packet inspection
4. **No adversarial testing** — Evasion attacks not evaluated
5. **Static model** — No online learning or concept drift handling

---

## 7. Ethical Considerations

- Dataset is publicly available for research
- No real network traffic or personal data used
- System intended for educational/defensive security only
- Misuse for offensive purposes is explicitly discouraged

---

## 8. References

1. Tavallaee, M., et al. (2009). *A detailed analysis of the KDD CUP 99 data set.* IEEE CISDA.
2. McHugh, J. (2000). *Testing intrusion detection systems.* ACM TISSEC.
3. Breiman, L. (2001). *Random Forests.* Machine Learning, 45(1).
4. Cortes, C. & Vapnik, V. (1995). *Support-vector networks.* Machine Learning, 20(3).
5. Pedregosa, F., et al. (2011). *Scikit-learn: Machine Learning in Python.* JMLR.

---

*Research Methodology Document v1.0*
