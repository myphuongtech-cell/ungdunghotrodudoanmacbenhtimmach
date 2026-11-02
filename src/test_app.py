"""Kiểm thử hàm dự đoán và giao diện; ghi bảng ca kiểm thử vào report/bang_kiem_thu.csv"""
import sys, time; from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
import pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
from src.predict import predict_risk, validate, get_model
from src.common import load_clean, FEATURES, TARGET
df = load_clean()
get_model()
def row(i): return df.loc[i, FEATURES].to_dict()
neg = df[(df[TARGET] == 0)].sort_values(["ca", "oldpeak", "age"]).index[0]
pos = df[(df[TARGET] == 1) & (df.ca >= 2)].sort_values("oldpeak", ascending=False).index[0]
mid = df.iloc[(df.index.to_series().map(lambda i: abs(predict_risk(row(i).copy() | {'ca': 0 if pd.isna(row(i)['ca']) else row(i)['ca'], 'thal': 2 if pd.isna(row(i)['thal']) else row(i)['thal']})[0] - 0.5))).argsort()[:1]].index[0]
base = {"age": 55, "sex": 1, "cp": 0, "trestbps": 130, "chol": 240, "fbs": 0, "restecg": 1, "thalach": 150, "exang": 0, "oldpeak": 1.0, "slope": 1, "ca": 0, "thal": 2}
fill = lambda i: {k: (v if not pd.isna(v) else base[k]) for k, v in row(i).items()}
cases = [
 ("T1", "Ca bình thường: bệnh nhân không bệnh trong dữ liệu, ít dấu hiệu", fill(neg), "Mức Thấp"),
 ("T2", "Ca bình thường: bệnh nhân có bệnh, nhiều mạch hẹp, oldpeak cao", fill(pos), "Mức Cao"),
 ("T3", "Ca gần ngưỡng: xác suất gần 50%", fill(mid), "Mức Trung bình hoặc Cao"),
 ("T4", "Biên dưới: mọi biến ở giá trị nhỏ nhất cho phép", {k: (RL[0]) for k, RL in __import__('src.predict', fromlist=['RULES']).RULES.items()}, "Chạy được, ra kết quả"),
 ("T5", "Biên trên: mọi biến ở giá trị lớn nhất cho phép", {k: (RL[1]) for k, RL in __import__('src.predict', fromlist=['RULES']).RULES.items()}, "Chạy được, ra kết quả"),
 ("T6", "Sai kiểu: tuổi nhập chữ", base | {"age": "abc"}, "Báo lỗi, không dự đoán"),
 ("T7", "Ngoài khoảng: tuổi 300", base | {"age": 300}, "Báo lỗi, không dự đoán"),
 ("T8", "Mã không hợp lệ: thal = 0", base | {"thal": 0}, "Báo lỗi, không dự đoán"),
 ("T9", "Thiếu trường: bỏ cholesterol", {k: v for k, v in base.items() if k != "chol"}, "Báo lỗi, không dự đoán"),
]
rows = []
for cid, desc, inp, exp in cases:
    t = time.perf_counter()
    try:
        p, lv = predict_risk(inp); res = f"Xác suất {p*100:.1f}%, mức {lv}"
        ok = (exp.startswith("Mức Thấp") and lv == "Thấp") or (exp.startswith("Mức Cao") and lv == "Cao") or \
             (exp.startswith("Mức Trung") and lv in ("Trung bình", "Cao")) or exp.startswith("Chạy được")
    except ValueError as e:
        res = f"Báo lỗi: {e}"; ok = exp.startswith("Báo lỗi")
    ms = (time.perf_counter() - t) * 1000
    rows.append({"Mã": cid, "Mô tả": desc, "Kết quả mong đợi": exp, "Kết quả thực tế": res, "Đạt": "Đạt" if ok else "KHÔNG đạt", "Thời gian (ms)": round(ms, 1)})
out = pd.DataFrame(rows); out.to_csv(Path(__file__).resolve().parents[1] / "report" / "bang_kiem_thu.csv", index=False)
pd.set_option("display.width", 250, "display.max_colwidth", 90); print(out.to_string(index=False))
# Kiểm thử giao diện
from streamlit.testing.v1 import AppTest
at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app" / "app.py")).run(timeout=60)
assert not at.exception, at.exception
btn = [b for b in at.button if b.label == "Dự đoán nguy cơ"][0]
btn.click().run(timeout=60)
assert not at.exception, at.exception
last = at.session_state["last"]
assert 0 <= last["p"] <= 1
print("UI: xác suất =", round(last["p"] * 100, 1), "% | mức:", last["level"], "| số dòng lịch sử:", len(at.session_state["history"]))
