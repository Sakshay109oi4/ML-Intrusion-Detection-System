"""
Real-Time Intrusion Detection GUI (Phase 6)
Simple Tkinter interface for manual feature input and live prediction.
Works on Windows without additional dependencies.
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.config import CATEGORICAL_COLUMNS, COLUMN_NAMES, TARGET_CLASSES
from src.prediction import get_default_feature_template, predict, format_prediction_result


# Dropdown options from NSL-KDD domain
PROTOCOL_OPTIONS = ["tcp", "udp", "icmp"]
SERVICE_OPTIONS = [
    "http", "smtp", "ftp", "ssh", "telnet", "domain", "eco_i", "private",
    "auth", "finger", "pop_3", "courier", "uucp", "time", "imap4", "ftp_data",
    "netbios_ns", "netbios_dgm", "netbios_ssn", "IRC", "X11", "shell",
    "login", "ldap", "ntp_u", "other", "red_i",
]
FLAG_OPTIONS = [
    "SF", "S0", "REJ", "RSTR", "RSTO", "S1", "S2", "S3", "SH", "OTH",
]


class IntrusionDetectionApp:
    """Tkinter GUI for real-time network intrusion classification."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("ML-Based Intrusion Detection System")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        self.entries: dict[str, tk.Variable] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        """Construct tabbed interface."""
        header = tk.Label(
            self.root,
            text="Network Intrusion Detection — Real-Time Classifier",
            font=("Segoe UI", 14, "bold"),
            pady=10,
        )
        header.pack()

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # Tab 1: Key features (quick input)
        quick_frame = ttk.Frame(notebook)
        notebook.add(quick_frame, text="Quick Input")
        self._build_quick_tab(quick_frame)

        # Tab 2: All features
        full_frame = ttk.Frame(notebook)
        notebook.add(full_frame, text="All Features")
        self._build_full_tab(full_frame)

        # Results panel
        result_label = tk.Label(self.root, text="Prediction Result", font=("Segoe UI", 11, "bold"))
        result_label.pack(pady=(5, 0))

        self.result_text = scrolledtext.ScrolledText(
            self.root, height=8, font=("Consolas", 10), state="disabled"
        )
        self.result_text.pack(fill="x", padx=10, pady=5)

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Detect Intrusion", command=self._on_predict).pack(
            side="left", padx=5
        )
        ttk.Button(btn_frame, text="Load Normal Sample", command=self._load_normal).pack(
            side="left", padx=5
        )
        ttk.Button(btn_frame, text="Load DoS Sample", command=self._load_dos).pack(
            side="left", padx=5
        )
        ttk.Button(btn_frame, text="Clear", command=self._clear).pack(side="left", padx=5)

    def _build_quick_tab(self, parent: ttk.Frame) -> None:
        """Essential features for quick classification."""
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        frame = ttk.Frame(canvas)

        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        quick_fields = [
            ("duration", "Duration", "0"),
            ("protocol_type", "Protocol", "tcp", "combo", PROTOCOL_OPTIONS),
            ("service", "Service", "http", "combo", SERVICE_OPTIONS[:15]),
            ("flag", "Flag", "SF", "combo", FLAG_OPTIONS),
            ("src_bytes", "Source Bytes", "0"),
            ("dst_bytes", "Destination Bytes", "0"),
            ("count", "Connection Count", "0"),
            ("srv_count", "Service Count", "0"),
            ("serror_rate", "SYN Error Rate", "0.0"),
            ("srv_serror_rate", "Service SYN Error Rate", "0.0"),
            ("same_srv_rate", "Same Service Rate", "0.0"),
            ("diff_srv_rate", "Different Service Rate", "0.0"),
        ]

        for i, field in enumerate(quick_fields):
            self._add_field(frame, field, row=i)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _build_full_tab(self, parent: ttk.Frame) -> None:
        """All 41 NSL-KDD features."""
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        frame = ttk.Frame(canvas)

        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        defaults = get_default_feature_template()
        feature_cols = [c for c in COLUMN_NAMES if c not in ["label", "difficulty"]]

        for i, col in enumerate(feature_cols):
            if col in CATEGORICAL_COLUMNS:
                options = PROTOCOL_OPTIONS if col == "protocol_type" else (
                    SERVICE_OPTIONS if col == "service" else FLAG_OPTIONS
                )
                self._add_field(
                    frame,
                    (col, col.replace("_", " ").title(), defaults[col], "combo", options),
                    row=i,
                )
            else:
                self._add_field(
                    frame,
                    (col, col.replace("_", " ").title(), str(defaults[col])),
                    row=i,
                )

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _add_field(self, parent, field_spec, row: int) -> None:
        """Add labeled input widget."""
        key = field_spec[0]
        label = field_spec[1]
        default = field_spec[2]
        widget_type = field_spec[3] if len(field_spec) > 3 else "entry"
        options = field_spec[4] if len(field_spec) > 4 else []

        ttk.Label(parent, text=label, width=28).grid(row=row, column=0, padx=5, pady=3, sticky="e")

        if widget_type == "combo":
            var = tk.StringVar(value=default)
            widget = ttk.Combobox(parent, textvariable=var, values=options, width=30)
        else:
            var = tk.StringVar(value=default)
            widget = ttk.Entry(parent, textvariable=var, width=33)

        widget.grid(row=row, column=1, padx=5, pady=3, sticky="w")
        self.entries[key] = var

    def _get_features(self) -> dict:
        """Collect all feature values from form."""
        defaults = get_default_feature_template()
        features = defaults.copy()

        for key, var in self.entries.items():
            val = var.get().strip()
            if key in CATEGORICAL_COLUMNS:
                features[key] = val
            else:
                try:
                    features[key] = float(val) if "." in val else int(val)
                except ValueError:
                    features[key] = 0
        return features

    def _show_result(self, text: str, prediction: str = "") -> None:
        """Display prediction in result panel with color coding."""
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, text)

        # Color tag based on prediction
        color_map = {
            "Normal Traffic": "#2ecc71",
            "DoS Attack": "#e74c3c",
            "Probe Attack": "#e67e22",
            "R2L Attack": "#9b59b6",
            "U2R Attack": "#c0392b",
        }
        if prediction in color_map:
            self.result_text.tag_configure("pred", foreground=color_map[prediction], font=("Consolas", 11, "bold"))
            start = text.find("Prediction:")
            if start >= 0:
                end = text.find("\n", start)
                self.result_text.tag_add("pred", f"1.0+{start}c", f"1.0+{end}c")

        self.result_text.config(state="disabled")

    def _on_predict(self) -> None:
        """Run prediction on user input."""
        try:
            features = self._get_features()
            result = predict(features)
            output = format_prediction_result(result)
            self._show_result(output, result["prediction"])
        except FileNotFoundError:
            messagebox.showerror(
                "Model Not Found",
                "Trained model not found.\nRun: python main.py --phase all",
            )
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _load_normal(self) -> None:
        """Populate form with normal traffic sample."""
        sample = get_default_feature_template()
        sample.update({
            "duration": 1, "protocol_type": "tcp", "service": "http", "flag": "SF",
            "src_bytes": 215, "dst_bytes": 4500, "count": 10, "srv_count": 10,
            "serror_rate": 0.0, "same_srv_rate": 1.0,
        })
        self._set_form(sample)

    def _load_dos(self) -> None:
        """Populate form with DoS-like sample."""
        sample = get_default_feature_template()
        sample.update({
            "duration": 0, "protocol_type": "tcp", "service": "http", "flag": "S0",
            "src_bytes": 0, "dst_bytes": 0, "count": 511, "srv_count": 511,
            "serror_rate": 1.0, "srv_serror_rate": 1.0, "same_srv_rate": 0.0,
        })
        self._set_form(sample)

    def _set_form(self, features: dict) -> None:
        """Set form values from feature dict."""
        for key, var in self.entries.items():
            if key in features:
                var.set(str(features[key]))

    def _clear(self) -> None:
        """Reset form to defaults."""
        defaults = get_default_feature_template()
        self._set_form(defaults)
        self._show_result("")


def main() -> None:
    root = tk.Tk()
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    IntrusionDetectionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
