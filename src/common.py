"""Hàm dùng chung cho các notebook (Đề tài 2: dự đoán nguy cơ bệnh tim mạch)."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA, FIG, MODELS = ROOT / "data", ROOT / "figures", ROOT / "models"
FIG.mkdir(exist_ok=True); MODELS.mkdir(exist_ok=True)
RANDOM_STATE = 42

sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams.update({"figure.dpi": 110, "savefig.dpi": 160, "axes.titleweight": "bold"})

NUMERIC = ["age", "trestbps", "chol", "thalach", "oldpeak", "ca"]
CATEGORICAL = ["cp", "restecg", "slope", "thal"]
BINARY = ["sex", "fbs", "exang"]
FEATURES = NUMERIC + CATEGORICAL + BINARY
TARGET = "HeartDisease"

VN = {"age": "Tuổi", "sex": "Giới tính", "cp": "Loại đau ngực", "trestbps": "Huyết áp nghỉ (mmHg)",
      "chol": "Cholesterol (mg/dl)", "fbs": "Đường huyết đói >120", "restecg": "Điện tâm đồ nghỉ",
      "thalach": "Nhịp tim tối đa", "exang": "Đau thắt ngực khi gắng sức", "oldpeak": "ST chênh xuống (oldpeak)",
      "slope": "Độ dốc đoạn ST", "ca": "Số mạch chính hẹp (0-3)", "thal": "Thalassemia"}

def savefig(name):
    plt.tight_layout(); plt.savefig(FIG / f"{name}.png", bbox_inches="tight"); plt.show()

def load_clean():
    return pd.read_csv(DATA / "heart_clean.csv")

def make_preprocessor():
    """Imputer + scaler + one-hot, fit CHỈ trên tập train khi nằm trong Pipeline (tránh rò rỉ dữ liệu)."""
    num = Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())])
    cat = Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                    ("oh", OneHotEncoder(handle_unknown="ignore", drop="if_binary"))])
    bin_ = Pipeline([("imp", SimpleImputer(strategy="most_frequent"))])
    return ColumnTransformer([("num", num, NUMERIC), ("cat", cat, CATEGORICAL), ("bin", bin_, BINARY)])
