import sys
from datetime import datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT)); sys.path.append(str(Path(__file__).resolve().parent))
import altair as alt
import pandas as pd
import streamlit as st
from src.predict import predict_risk, explain, RULES, LOW, HIGH, META
import style as S

st.set_page_config(page_title="CardioCheck: nguy cơ bệnh tim mạch", page_icon="🫀", layout="wide")
st.markdown(S.css(LOW, HIGH), unsafe_allow_html=True)
st.markdown(S.topbar(), unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv(ROOT / "data" / "heart_clean.csv")

@st.cache_data
def load_cmp():
    return pd.read_csv(ROOT / "report" / "bang_so_sanh_cv_lap.csv", encoding="utf-8")

st.session_state.setdefault("history", [])
st.session_state.setdefault("last", None)

SAMPLES = {
    "low": dict(age=38, sex=0, cp=2, trestbps=118, chol=190, fbs=0, restecg=0, thalach=175, exang=0, oldpeak=0.0, slope=2, ca=0, thal=2),
    "high": dict(age=62, sex=1, cp=0, trestbps=150, chol=270, fbs=1, restecg=1, thalach=110, exang=1, oldpeak=3.2, slope=0, ca=3, thal=3),
}
DEFAULT = dict(age=55, sex=1, cp=0, trestbps=130, chol=240, fbs=0, restecg=1, thalach=150, exang=0, oldpeak=1.0, slope=1, ca=0, thal=2)
for k, v in DEFAULT.items():
    st.session_state.setdefault(f"in_{k}", v)

def fill(name):
    for k, v in SAMPLES[name].items():
        st.session_state[f"in_{k}"] = v

ORANGE, INK = S.ORANGE, S.INK
def tidy(ch):
    return (ch.configure(background="transparent").configure_view(stroke=None)
              .configure_axis(labelColor="#6b6b6b", titleColor="#6b6b6b", gridColor="#e9e9e9", domain=False, tickSize=0, labelFontSize=12))

tab_over, tab_pred, tab_model = st.tabs(["Tổng quan", "Dự đoán", "Mô hình"])

# ---------------------------------------------------------------- TỔNG QUAN
with tab_over:
    df = load_data()
    st.markdown('<div class="hello">Xin chào 👋</div><div class="sub">Theo dõi dữ liệu, hiệu năng mô hình và các lần dự đoán gần đây của bạn.</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.05, 1.15, 1.3])
    nest = META["nested_threshold_metrics"]; cv = META["cv5x5_metrics"]
    with c1:
        st.markdown(f"""<div class="card" style="height:100%"><h4>Ngưỡng cảnh báo</h4><div class="hint">Xác suất nguy cơ được chia thành ba mức</div>
        <div style="font-size:40px;font-weight:700;letter-spacing:-.03em">{LOW:.0%} <span style="font-size:16px;color:#6b6b6b;font-weight:500">ngưỡng sàng lọc</span></div>
        {S.zones(None, LOW, HIGH)}
        <div class="note">Dưới {LOW:.0%}: mức Thấp. Ngưỡng được chọn bằng dữ liệu để mô hình phát hiện khoảng 90% ca có bệnh (nested CV); đổi lại khoảng một phần tư ca báo có bệnh là báo nhầm. Mức Cao từ {HIGH:.0%} là quy ước của bài.</div></div>""", unsafe_allow_html=True)
    with c2:
        a, b = st.columns(2)
        a.markdown(S.stat("Bệnh nhân", f"{len(df)}", "Sau khi xóa 1 dòng trùng", hot=True), unsafe_allow_html=True)
        b.markdown(S.stat("Có bệnh", f"{df.HeartDisease.mean()*100:.1f}%".replace(".", ","), f"{int(df.HeartDisease.sum())} / {len(df)} người"), unsafe_allow_html=True)
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        a, b = st.columns(2)
        a.markdown(S.stat("Recall (sàng lọc)", S.vn(nest["Recall"], 2), f"Precision {S.vn(nest['Precision'], 2)}"), unsafe_allow_html=True)
        b.markdown(S.stat("ROC-AUC", S.vn(cv["roc_auc"], 3), "CV lặp 5x5"), unsafe_allow_html=True)
    with c3:
        d = df.copy()
        d["Nhóm tuổi"] = pd.cut(d.age, [0, 44, 54, 64, 120], labels=["<45", "45-54", "55-64", "≥65"])
        d["Nhãn"] = d.HeartDisease.map({1: "Có bệnh", 0: "Không bệnh"})
        g = d.groupby(["Nhóm tuổi", "Nhãn"], observed=True).size().reset_index(name="Số bệnh nhân")
        chart = alt.Chart(g).mark_bar(cornerRadiusTopLeft=7, cornerRadiusTopRight=7, size=44).encode(
            x=alt.X("Nhóm tuổi:N", sort=["<45", "45-54", "55-64", "≥65"], axis=alt.Axis(labelAngle=0, title=None)),
            y=alt.Y("Số bệnh nhân:Q", title=None),
            color=alt.Color("Nhãn:N", scale=alt.Scale(domain=["Không bệnh", "Có bệnh"], range=[INK, ORANGE]), legend=None),
            order=alt.Order("Nhãn:N", sort="descending"), tooltip=["Nhóm tuổi", "Nhãn", "Số bệnh nhân"]).properties(height=190)
        with st.container(key="card_chart"):
            st.markdown('<h4 style="margin:0 0 2px;font-size:19px;font-weight:600">Phân bố theo nhóm tuổi</h4><div class="hint">Số bệnh nhân có và không có bệnh tim</div>'
                        '<div class="legend"><span style="--c:#e8603c">Có bệnh</span><span style="--c:#1b1b1b">Không bệnh</span></div>', unsafe_allow_html=True)
            st.altair_chart(tidy(chart), width="stretch")
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    rows = ""
    for h in reversed(st.session_state.history[-6:]):
        rows += f"<tr><td>{h['time']}</td><td>{h['who']}</td><td>{h['p']*100:.1f}%</td><td>{S.level_pill(h['level'])}</td></tr>".replace("<td>", "<td>", 1)
    body = (f'<table class="tbl"><tr><th>Thời gian</th><th>Bệnh nhân</th><th>Xác suất</th><th>Mức cảnh báo</th></tr>{rows}</table>' if rows
            else '<div class="empty">Chưa có dự đoán nào trong phiên này. Mở tab <b>Dự đoán</b> để thử.</div>')
    st.markdown(f'<div class="card"><h4>Dự đoán gần đây</h4><div class="hint">Chỉ lưu trong phiên làm việc hiện tại, đóng trình duyệt là mất</div>{body}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------- DỰ ĐOÁN
with tab_pred:
    st.markdown('<div class="hello">Dự đoán nguy cơ</div><div class="sub">Nhập 13 chỉ số lâm sàng. Kết quả chỉ mang tính tham khảo.</div>', unsafe_allow_html=True)
    left, right = st.columns([1.15, 1])
    with left:
        with st.container(key="card_form"):
            b1, b2, _ = st.columns([1, 1, 1.4])
            b1.button("Ca minh họa: thấp", on_click=fill, args=("low",), width="stretch")
            b2.button("Ca minh họa: cao", on_click=fill, args=("high",), width="stretch")
            with st.form("form"):
                st.markdown('<div class="section-lbl">Thông tin chung</div>', unsafe_allow_html=True)
                x1, x2, x3 = st.columns(3)
                age = x1.number_input("Tuổi", *RULES["age"], key="in_age")
                sex = x2.selectbox("Giới tính", [0, 1], format_func=lambda v: "Nữ" if v == 0 else "Nam", key="in_sex")
                trestbps = x3.number_input("Huyết áp nghỉ (mmHg)", *RULES["trestbps"], key="in_trestbps")
                st.markdown('<div class="section-lbl">Xét nghiệm</div>', unsafe_allow_html=True)
                y1, y2, y3 = st.columns(3)
                chol = y1.number_input("Cholesterol (mg/dl)", *RULES["chol"], key="in_chol")
                fbs = y2.selectbox("Đường huyết đói > 120", [0, 1], format_func=lambda v: "Không" if v == 0 else "Có", key="in_fbs")
                restecg = y3.selectbox("Điện tâm đồ nghỉ (mã 0-2)", [0, 1, 2], key="in_restecg")
                st.markdown('<div class="section-lbl">Triệu chứng và khám gắng sức</div>', unsafe_allow_html=True)
                z1, z2, z3 = st.columns(3)
                cp = z1.selectbox("Loại đau ngực (mã 0-3)", [0, 1, 2, 3], key="in_cp")
                exang = z2.selectbox("Đau ngực khi gắng sức", [0, 1], format_func=lambda v: "Không" if v == 0 else "Có", key="in_exang")
                thalach = z3.number_input("Nhịp tim tối đa", *RULES["thalach"], key="in_thalach")
                w1, w2, w3 = st.columns(3)
                oldpeak = w1.number_input("ST chênh xuống", 0.0, 7.0, step=0.1, key="in_oldpeak")
                slope = w2.selectbox("Độ dốc đoạn ST (mã 0-2)", [0, 1, 2], key="in_slope")
                ca = w3.selectbox("Số mạch hẹp (0-3)", [0, 1, 2, 3], key="in_ca")
                thal = st.selectbox("Thalassemia (mã 1-3)", [1, 2, 3], key="in_thal")
                go = st.form_submit_button("Dự đoán nguy cơ")
            if go:
                inp = dict(age=age, sex=sex, cp=cp, trestbps=trestbps, chol=chol, fbs=fbs, restecg=restecg, thalach=thalach, exang=exang,
                           oldpeak=oldpeak, slope=slope, ca=ca, thal=thal)
                try:
                    p, lv = predict_risk(inp)
                    st.session_state.last = dict(p=p, level=lv, ex=explain(inp))
                    st.session_state.history.append(dict(time=datetime.now().strftime("%H:%M:%S"), who=f"{'Nam' if sex == 1 else 'Nữ'}, {int(age)} tuổi", p=p, level=lv))
                except ValueError as e:
                    st.session_state.last = dict(error=str(e))
    with right:
        last = st.session_state.last
        with st.container(key="card_result"):
            if last is None:
                st.markdown('<div class="card" style="border:none;padding:0"><h4>Kết quả</h4><div class="empty">Nhập chỉ số rồi bấm <b>Dự đoán nguy cơ</b>.<br>Hoặc dùng nút “Ca minh họa” để thử nhanh.</div></div>', unsafe_allow_html=True)
            elif "error" in last:
                st.error(last["error"])
            else:
                p, lv = last["p"], last["level"]
                bg, fg, dot = S.LEVEL_STYLE[lv]
                st.markdown(f"""<div class="stat hot" style="margin-bottom:16px"><div class="lbl">Xác suất nguy cơ theo mô hình</div>
                    <div class="num" style="font-size:64px">{p*100:.1f}%</div>
                    <span class="badge" style="background:#fff;color:{fg}">● Mức {lv}</span></div>""", unsafe_allow_html=True)
                st.markdown(S.zones(p, LOW, HIGH), unsafe_allow_html=True)
                ex = last["ex"].head(6).reset_index(); ex.columns = ["Yếu tố", "Đóng góp"]
                ex["Hướng"] = ex["Đóng góp"].map(lambda v: "Tăng nguy cơ" if v > 0 else "Giảm nguy cơ")
                ch = alt.Chart(ex).mark_bar(cornerRadiusEnd=6, size=18).encode(
                    y=alt.Y("Yếu tố:N", sort=None, axis=alt.Axis(title=None, labelLimit=170)), x=alt.X("Đóng góp:Q", title=None),
                    color=alt.Color("Hướng:N", scale=alt.Scale(domain=["Tăng nguy cơ", "Giảm nguy cơ"], range=[ORANGE, INK]), legend=None),
                    tooltip=["Yếu tố", alt.Tooltip("Đóng góp:Q", format=".2f"), "Hướng"]).properties(height=210)
                st.markdown('<h4 style="margin:22px 0 2px;font-size:19px;font-weight:600">Vì sao có kết quả này?</h4><div class="legend"><span style="--c:#e8603c">Làm tăng nguy cơ</span><span style="--c:#1b1b1b">Làm giảm nguy cơ</span></div>', unsafe_allow_html=True)
                st.altair_chart(tidy(ch), width="stretch")
                st.markdown(f'<div class="note">Đóng góp tính so với bệnh nhân trung bình trong dữ liệu (log-odds, tương đương SHAP của mô hình tuyến tính). Mức Thấp nghĩa là dưới {LOW:.0%}. Xác suất chưa được hiệu chỉnh hoàn hảo (hơi cao ở vùng thấp). Nếu có triệu chứng hoặc lo ngại, hãy gặp bác sĩ.</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------- MÔ HÌNH
with tab_model:
    st.markdown('<div class="hello">Về mô hình</div><div class="sub">Logistic Regression, đánh giá bằng cross-validation lặp 5x5 trên 302 bệnh nhân.</div>', unsafe_allow_html=True)
    cmp_ = load_cmp()
    m1, m2 = st.columns([1.5, 1])
    with m1:
        rows = ""
        for _, r in cmp_.iterrows():
            chosen = r["Mô hình"] == "Logistic Regression"
            name = f"<b>{r['Mô hình']}</b> <span class='badge' style='background:#1b1b1b;color:#fff'>đang dùng</span>" if chosen else r["Mô hình"]
            rows += f"<tr><td>{name}</td><td>{r['recall'].replace('.', ',')}</td><td>{r['f2'].replace('.', ',')}</td><td>{r['roc_auc'].replace('.', ',')}</td></tr>"
        st.markdown(f'<div class="card"><h4>So sánh mô hình</h4><div class="hint">Trung bình ± độ lệch chuẩn qua 25 lần chia. Các mô hình hòa nhau, bài chọn mô hình đơn giản và giải thích được.</div>'
                    f'<table class="tbl"><tr><th>Mô hình</th><th>Recall</th><th>F2</th><th>ROC-AUC</th></tr>{rows}</table></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="card" style="height:100%"><h4>Giới hạn cần nhớ</h4><div class="hint">Đọc trước khi dùng kết quả</div>
        <ul style="padding-left:18px;line-height:1.7;font-size:14px;margin:0">
        <li>Dữ liệu nhỏ: 302 bệnh nhân, một cơ sở y tế ở Mỹ, thu thập từ thập niên 1980</li>
        <li>Chưa kiểm chứng trên người Việt Nam</li>
        <li>Chưa đủ dữ liệu để kiểm tra công bằng theo giới</li>
        <li>Một số chỉ số (số mạch hẹp, thalassemia, ST) cần khám chuyên khoa</li>
        <li>Không dùng để chẩn đoán hay quyết định điều trị</li></ul></div>""", unsafe_allow_html=True)
