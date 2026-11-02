"""Hàm dự đoán dùng cho ứng dụng và kiểm thử."""
import json, joblib
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ["age", "trestbps", "chol", "thalach", "oldpeak", "ca", "cp", "restecg", "slope", "thal", "sex", "fbs", "exang"]
# Khoảng hợp lệ (lấy theo mô tả cột; tuổi/huyết áp... mở rộng nhẹ hơn dữ liệu huấn luyện)
RULES = {"age": (18, 100), "trestbps": (80, 250), "chol": (100, 600), "thalach": (60, 220), "oldpeak": (0, 7),
         "ca": (0, 3), "cp": (0, 3), "restecg": (0, 2), "slope": (0, 2), "thal": (1, 3), "sex": (0, 1), "fbs": (0, 1), "exang": (0, 1)}
META = json.loads((ROOT / "models" / "model_final_meta.json").read_text(encoding="utf-8"))
LOW = META["threshold_screening"]   # ngưỡng sàng lọc: chọn để Recall >= 0,90 (notebook 04)
HIGH = META["threshold_high"]       # quy ước của bài cho mức "Cao"

_model = None
def get_model():
    global _model
    if _model is None:
        _model = joblib.load(ROOT / "models" / "model_final.joblib")
    return _model

def validate(d):
    missing = [f for f in FEATURES if f not in d or d[f] is None or d[f] == ""]
    if missing: raise ValueError(f"Thiếu giá trị: {', '.join(missing)}")
    out = {}
    for f in FEATURES:
        try: v = float(d[f])
        except (TypeError, ValueError): raise ValueError(f"'{f}' phải là số, nhận được {d[f]!r}")
        lo, hi = RULES[f]
        if not lo <= v <= hi: raise ValueError(f"'{f}' = {v:g} ngoài khoảng hợp lệ [{lo}, {hi}]")
        out[f] = v
    return out

def level(p):
    return "Thấp" if p < LOW else ("Trung bình" if p < HIGH else "Cao")

def predict_risk(d):
    x = pd.DataFrame([validate(d)])[FEATURES]
    p = float(get_model().predict_proba(x)[0, 1])
    return p, level(p)

FEATURE_VN = {"age": "Tuổi", "sex": "Giới tính", "cp": "Loại đau ngực", "trestbps": "Huyết áp nghỉ", "chol": "Cholesterol",
              "fbs": "Đường huyết đói", "restecg": "Điện tâm đồ nghỉ", "thalach": "Nhịp tim tối đa", "exang": "Đau ngực khi gắng sức",
              "oldpeak": "ST chênh xuống", "slope": "Độ dốc đoạn ST", "ca": "Số mạch hẹp", "thal": "Thalassemia"}

def _orig(n):
    kind, rest = n.split("__", 1)
    return rest.rsplit("_", 1)[0] if kind == "cat" else rest

def explain(d):
    """Đóng góp của từng đặc trưng vào log-odds so với bệnh nhân trung bình (Logistic Regression: tương đương SHAP tuyến tính).
    Dương = làm tăng nguy cơ, âm = làm giảm nguy cơ."""
    m = get_model(); x = pd.DataFrame([validate(d)])[FEATURES]
    z = m.named_steps["prep"].transform(x)[0]
    contrib = m.named_steps["clf"].coef_[0] * (z - __import__("numpy").array(META["ref_means"]))
    s = pd.Series(contrib, index=[_orig(n) for n in META["transformed_names"]]).groupby(level=0).sum()
    s.index = [FEATURE_VN[i] for i in s.index]
    return s.sort_values(key=abs, ascending=False)
