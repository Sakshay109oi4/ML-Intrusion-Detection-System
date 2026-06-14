# Installation Guide — ML-Based Intrusion Detection System

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| OS | Windows 10/11 | Windows 11 |
| Python | 3.9 | 3.10 or 3.11 |
| RAM | 4 GB | 8 GB |
| Disk Space | 500 MB | 1 GB |
| Internet | Required (first run) | — |

---

## Step 1: Install Python

1. Download Python from [python.org/downloads](https://www.python.org/downloads/)
2. During installation, **check "Add Python to PATH"**
3. Verify installation:

```powershell
python --version
pip --version
```

Expected output: `Python 3.9.x` or higher.

---

## Step 2: Get Project Files

If using Git:

```powershell
git clone <repository-url>
cd ml-intrusion-detection-system
```

Or extract the ZIP to a folder such as:
`C:\Users\Sakshay\ml-intrusion-detection-system`

---

## Step 3: Create Virtual Environment (Recommended)

```powershell
cd C:\Users\Sakshay\ml-intrusion-detection-system
python -m venv venv
```

Activate the environment:

```powershell
# PowerShell
.\venv\Scripts\Activate.ps1

# Command Prompt
venv\Scripts\activate.bat
```

If PowerShell blocks script execution:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Step 4: Install Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

Verify packages:

```powershell
python -c "import pandas, sklearn, matplotlib, seaborn, joblib; print('All packages OK')"
```

---

## Step 5: Run the Pipeline

### Full Pipeline (First Time)

```powershell
python main.py --phase all
```

What happens:
1. Downloads NSL-KDD train/test files (~18 MB total)
2. Preprocesses 125K+ training records
3. Generates 8+ visualization charts
4. Trains 4 ML models
5. Evaluates and saves best model

### If Download Fails

1. Visit: https://github.com/DefCode/NSL-KDD
2. Download `KDDTrain+.txt` and `KDDTest+.txt`
3. Place both files in `data/raw/`
4. Re-run: `python main.py --phase all`

---

## Step 6: Launch GUI

After training completes:

```powershell
python main.py --gui
```

Use **Quick Input** tab for essential features or **All Features** for complete NSL-KDD input.

---

## Step 7: Verify Installation

Check these files exist after pipeline run:

```
models/best_ids_model.joblib          ✓
models/preprocessor.joblib            ✓
outputs/figures/model_comparison.png  ✓
outputs/metrics/evaluation_results.json ✓
```

Run demo prediction:

```powershell
python main.py --phase predict
```

---

## Common Issues on Windows

### Issue: `'python' is not recognized`

- Reinstall Python with "Add to PATH" checked
- Or use full path: `C:\Users\<You>\AppData\Local\Programs\Python\Python311\python.exe`

### Issue: `ModuleNotFoundError: No module named 'config'`

Always run from project root:

```powershell
cd C:\Users\Sakshay\ml-intrusion-detection-system
python main.py --phase all
```

### Issue: Matplotlib display errors

Plots are saved to files, not displayed. Check `outputs/figures/`.

### Issue: Training takes too long

- Close other applications to free RAM
- SVM is the slowest model; others finish in minutes

---

## Uninstall / Clean Reset

```powershell
# Remove generated artifacts
Remove-Item -Recurse -Force models\*, outputs\*, data\processed\*
Remove-Item -Force data\raw\*.txt

# Deactivate and remove venv
deactivate
Remove-Item -Recurse -Force venv
```

---

## Support

Refer to:
- `README.md` — Project overview
- `docs/PROJECT_REPORT.md` — Technical details
- `docs/VIVA_QUESTIONS.md` — Common interview questions
