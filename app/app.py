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

st.set_page_config(page_title="ỨNG DỤNG HỖ TRỢ DỰ ĐOÁN MẮC BỆNH TIM MẠCH", page_icon="🫀", layout="wide")
st.markdown(S.css(LOW, HIGH), unsafe_allow_html=True)
st.markdown(S.topbar(), unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv(ROOT / "data" / "heart_clean.csv")

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

# Cấu trúc 3 Tab hoàn toàn thuần chất Y tế & Sức khỏe
tab_over, tab_pred, tab_advice = st.tabs(["TỔNG QUAN", "DỰ ĐOÁN", "TƯ VẤN"])

# ---------------------------------------------------------------- TAB 1: TỔNG QUAN SỨC KHỎE CỘNG ĐỒNG
with tab_over:
    df = load_data()
    st.markdown('<div class="hello">Đường đến một trái tim khỏe mạnh được lát bằng những ý định tốt và những lựa chọn tích cực</div><div class="sub">Hãy theo dõi dữ liệu sức khỏe tim mạch hằng ngày nhé!</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1.05, 1.15, 1.3])
    with c1:
        st.markdown(
            f"""
            <div class="card" style="height:100%">
                <h4>Ngưỡng phân loại nguy cơ</h4>
                <div class="hint">Hệ thống phân tầng mức độ rủi ro sức khỏe</div>
                <div style="font-size:40px;font-weight:700;letter-spacing:-.03em">
                    {LOW:.0%} <span style="font-size:16px;color:#6b6b6b;font-weight:500">ngưỡng tầm soát</span>
                </div>
                {S.zones(None, LOW, HIGH)}
                <div class="note">
                    • Dưới {LOW:.0%}: Nguy cơ thấp (Đi khám định kỳ mỗi 6 tháng một lần, duy trì lối sống lành mạnh).<br>
                    • Từ {LOW:.0%} đến {HIGH:.0%}: Nguy cơ trung bình (Cần theo dõi sát sao các chỉ số).<br>
                    • Từ {HIGH:.0%} trở lên: Nguy cơ cao (Báo động đỏ, cần phải được đi thăm khám chuyên khoa tim mạch càng sớm càng tốt).
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    with c2:
        # Lấy lịch sử tầm soát của người dùng trong phiên để hiển thị số liệu cá nhân
        history = st.session_state.history
        total_checks = len(history)
        last_risk = f"{history[-1]['p']*100:.1f}% ({history[-1]['level']})" if history else "Chưa có"
        
        a, b = st.columns(2)
        a.markdown(S.stat("Lần tầm soát", f"{total_checks} lần", "Đã thực hiện trong phiên", hot=True), unsafe_allow_html=True)
        b.markdown(S.stat("Kết quả gần nhất", last_risk, "Cập nhật lần kiểm tra gần đây"), unsafe_allow_html=True)
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        
        a, b = st.columns(2)
        a.markdown(S.stat("Trạng thái", "Sẵn sàng", "Hệ thống ghi nhận bình thường"), unsafe_allow_html=True)
        b.markdown(S.stat("Mục tiêu theo dõi", "Huyết áp & Mỡ máu", "Khuyến nghị kiểm tra định kỳ"), unsafe_allow_html=True)
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
            st.markdown('<h4 style="margin:0 0 2px;font-size:19px;font-weight:600">Phân bố bệnh lý theo nhóm tuổi</h4><div class="hint">Thống kê tỷ lệ mắc bệnh tim mạch trên cơ sở dữ liệu</div>'
                        '<div class="legend"><span style="--c:#e8603c">Bệnh lý tim mạch</span><span style="--c:#1b1b1b">Bình thường</span></div>', unsafe_allow_html=True)
            st.altair_chart(tidy(chart), width="stretch")
            
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    rows = ""
    for h in reversed(st.session_state.history[-6:]):
        rows += f"<tr><td>{h['time']}</td><td>{h['who']}</td><td>{h['p']*100:.1f}%</td><td>{S.level_pill(h['level'])}</td></tr>"
    body = (f'<table class="tbl"><tr><th>Thời gian</th><th>Hồ sơ đánh giá</th><th>Xác suất nguy cơ</th><th>Mức độ</th></tr>{rows}</table>' if rows
            else '<div class="empty">Chưa có lịch sử tầm soát trong phiên làm việc này. Hãy chuyển sang tab <b>Sàng lọc & Đánh giá Nguy cơ</b> để bắt đầu.</div>')
    st.markdown(f'<div class="card"><h4>Lịch sử tầm soát gần đây</h4><div class="hint">Lưu trữ tạm thời trong phiên làm việc hiện tại của bạn</div>{body}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------- TAB 2: SÀNG LỌC & ĐÁNH GIÁ NGUY CƠ
with tab_pred:
    st.markdown('<div class="hello">Đánh giá tim mạch cá nhân</div><div class="sub">Nhập các thông số sinh hóa và triệu chứng lâm sàng để hệ thống phân tích mức độ rủi ro sức khỏe.</div>', unsafe_allow_html=True)
    left, right = st.columns([1.15, 1])
    with left:
        with st.container(key="card_form"):
            b1, b2, _ = st.columns([1, 1, 1.4])
            b1.button("Hồ sơ mẫu: Nguy cơ thấp", on_click=fill, args=("low",), width="stretch")
            b2.button("Hồ sơ mẫu: Nguy cơ cao", on_click=fill, args=("high",), width="stretch")
            with st.form("form"):
                st.markdown('<div class="section-lbl">1. Thông tin Nhân khẩu học & Huyết động</div>', unsafe_allow_html=True)
                x1, x2 = st.columns(2)
                age = x1.number_input("Tuổi", *RULES["age"], key="in_age")
                sex = x2.selectbox("Giới tính", [0, 1], format_func=lambda v: "Nữ" if v == 0 else "Nam", key="in_sex")
                trestbps = x1.number_input("Huyết áp tâm thu (mmHg)", *RULES["trestbps"], key="in_trestbps")
                
                st.markdown('<div class="section-lbl">2. Chỉ số Sinh hóa & Xét nghiệm</div>', unsafe_allow_html=True)
                y1, y2 = st.columns(2)
                chol = y1.number_input("Cholesterol toàn phần (mg/dl)", *RULES["chol"], key="in_chol")
                fbs = y2.selectbox("Đường huyết đói", [0, 1], format_func=lambda v: "Bình thường (≤ 120 mg/dl)" if v == 0 else "Cao (> 120 mg/dl)", key="in_fbs")
                
                restecg = st.selectbox("Kết quả Điện tâm đồ nghỉ (ECG)", [0, 1, 2], format_func=lambda v: {0: "Bình thường", 1: "Có bất thường sóng ST-T", 2: "Phì đại cơ thất trái"}[v], key="in_restecg")
                
                st.markdown('<div class="section-lbl">3. Triệu chứng & Khảo sát Gắng sức</div>', unsafe_allow_html=True)
                cp = st.selectbox("Triệu chứng đau ngực cụ thể", [0, 1, 2, 3], format_func=lambda v: {
                    0: "Đau thắt ngực điển hình (Đau tức khi gắng sức, giảm khi nghỉ)", 
                    1: "Đau thắt ngực không điển hình", 
                    2: "Đau ngực không do tim", 
                    3: "Không có triệu chứng đau ngực"
                }[v], key="in_cp")
                
                z1, z2 = st.columns(2)
                exang = z1.selectbox("Đau ngực khi vận động/gắng sức", [0, 1], format_func=lambda v: "Không" if v == 0 else "Có", key="in_exang")
                thalach = z2.number_input("Nhịp tim tối đa khi gắng sức", *RULES["thalach"], key="in_thalach")
                
                w1, w2 = st.columns(2)
                oldpeak = w1.number_input("Độ chênh đoạn ST (Oldpeak)", 0.0, 7.0, step=0.1, key="in_oldpeak")
                slope = w2.selectbox("Độ dốc đoạn ST gắng sức", [0, 1, 2], format_func=lambda v: {0: "Dốc lên", 1: "Bằng phẳng", 2: "Dốc xuống"}[v], key="in_slope")
                
                ca = st.selectbox("Số lượng mạch máu chính bị hẹp (0-3)", [0, 1, 2, 3], key="in_ca")
                thal = st.selectbox("Tình trạng lưu lượng máu (Thalassemia)", [1, 2, 3], format_func=lambda v: {1: "Bình thường", 2: "Khuyết tật cố định", 3: "Khuyết tật hồi phục"}[v], key="in_thal")
                
                go = st.form_submit_button("Thực hiện Đánh giá Nguy cơ")
            if go:
                if age < 18:
                    st.warning("⚠️ Lưu ý: Hệ thống được thiết kế dựa trên cơ sở dữ liệu lâm sàng của người trưởng thành (từ 18 tuổi trở lên). Kết quả cho độ tuổi dưới 18 chỉ mang tính chất tham khảo.")
                
                inp = dict(age=age, sex=sex, cp=cp, trestbps=trestbps, chol=chol, fbs=fbs, restecg=restecg, thalach=thalach, exang=exang,
                           oldpeak=oldpeak, slope=slope, ca=ca, thal=thal)
                try:
                    p, lv = predict_risk(inp)
                    st.session_state.last = dict(p=p, level=lv, ex=explain(inp), inputs=inp)
                    st.session_state.history.append(dict(time=datetime.now().strftime("%H:%M:%S"), who=f"{'Nam' if sex == 1 else 'Nữ'}, {int(age)} tuổi", p=p, level=lv))
                except ValueError as e:
                    st.session_state.last = dict(error=str(e))
    with right:
        last = st.session_state.last
        with st.container(key="card_result"):
            if last is None:
                st.markdown('<div class="card" style="border:none;padding:0"><h4>Kết quả phân tích</h4><div class="empty">Vui lòng nhập đầy đủ các chỉ số bên trái và bấm nút <b>Thực hiện Đánh giá Nguy cơ</b>.<br>Hoặc chọn nhanh hồ sơ mẫu phía trên để xem thử kết quả.</div></div>', unsafe_allow_html=True)
            elif "error" in last:
                st.error(last["error"])
            else:
                p, lv = last["p"], last["level"]
                inp_data = last.get("inputs", {})
                bg, fg, dot = S.LEVEL_STYLE[lv]
                
                st.markdown(f"""<div class="stat hot" style="margin-bottom:16px"><div class="lbl">Xác suất nguy cơ bệnh tim mạch</div>
                    <div class="num" style="font-size:64px">{p*100:.1f}%</div>
                    <span class="badge" style="background:#fff;color:{fg}">● Mức độ: {lv}</span></div>""", unsafe_allow_html=True)
                st.markdown(S.zones(p, LOW, HIGH), unsafe_allow_html=True)
                
                st.markdown(f'<div class="note" style="background:#f8f9fa;padding:12px;border-radius:12px;margin-top:14px"><b>Nhận định lâm sàng:</b> Mức độ rủi ro được ghi nhận ở cấp độ <b>{lv}</b> dựa trên việc tổng hợp toàn diện các thông số sinh hóa và triệu chứng bạn vừa cung cấp.</div>', unsafe_allow_html=True)
                
                # --- PHẦN PHÂN TÍCH THỰC TẾ CÁC CHỈ SỐ LÂM SÀNG & SINH HÓA ---
                st.markdown('<h4 style="margin:20px 0 8px;font-size:17px;font-weight:600">Phân tích Chi tiết Các Chỉ số Sức khỏe</h4>', unsafe_allow_html=True)
                
                # Phân tích huyết áp
                bp = inp_data.get('trestbps', 120)
                bp_eval = "Huyết áp bình thường" if bp <= 120 else ("Huyết áp tiền cao huyết áp" if bp <= 139 else "Huyết áp cao (Cần theo dõi sát)")
                bp_color = "#2e7d32" if bp <= 120 else ("#f57c00" if bp <= 139 else "#c62828")
                
                # Phân tích cholesterol
                cl = inp_data.get('chol', 200)
                cl_eval = "Mức mỡ máu lý tưởng" if cl < 200 else ("Mức ranh giới cần lưu ý" if cl <= 239 else "Cholesterol máu cao (Nguy cơ xơ vữa)")
                cl_color = "#2e7d32" if cl < 200 else ("#f57c00" if cl <= 239 else "#c62828")
                
                # Phân tích đau ngực & gắng sức
                cp_val = inp_data.get('cp', 3)
                cp_text = {0: "Có triệu chứng đau thắt ngực điển hình khi vận động", 1: "Có triệu chứng đau thắt ngực không điển hình", 2: "Đau ngực không do tim mạch", 3: "Không có triệu chứng đau ngực"}.get(cp_val, "")
                
                analysis_html = f"""
                <div style="background:#fdfdfd;border:1px solid #e0e0e0;padding:14px;border-radius:10px;font-size:14px;line-height:1.6;">
                    • <b>Huyết áp tâm thu ({bp} mmHg):</b> <span style="color:{bp_color};font-weight:600;">{bp_eval}</span>.<br>
                    • <b>Cholesterol toàn phần ({cl} mg/dl):</b> <span style="color:{cl_color};font-weight:600;">{cl_eval}</span>.<br>
                    • <b>Triệu chứng lâm sàng:</b> {cp_text}.<br>
                    • <b>Đánh giá tổng quan thói quen & gắng sức:</b> Nhịp tim tối đa và các chỉ số điện tâm đồ gắng sức phản ánh khả năng đáp ứng của hệ tuần hoàn khi cơ thể hoạt động cường độ cao.
                </div>
                """
                st.markdown(analysis_html, unsafe_allow_html=True)
                
                ex = last["ex"].head(5).reset_index(); ex.columns = ["Yếu tố", "Đóng góp"]
                ex["Hướng"] = ex["Đóng góp"].map(lambda v: "Làm tăng nguy cơ" if v > 0 else "Giảm nguy cơ")
                ch = alt.Chart(ex).mark_bar(cornerRadiusEnd=6, size=16).encode(
                    y=alt.Y("Yếu tố:N", sort=None, axis=alt.Axis(title=None, labelLimit=170)), x=alt.X("Đóng góp:Q", title=None),
                    color=alt.Color("Hướng:N", scale=alt.Scale(domain=["Làm tăng nguy cơ", "Làm giảm nguy cơ"], range=[ORANGE, INK]), legend=None),
                    tooltip=["Yếu tố", alt.Tooltip("Đóng góp:Q", format=".2f"), "Hướng"]).properties(height=160)
                st.markdown('<h4 style="margin:20px 0 2px;font-size:17px;font-weight:600">Các yếu tố chi phối sức khỏe</h4><div class="legend"><span style="--c:#e8603c">Yếu tố làm tăng rủi ro</span><span style="--c:#1b1b1b">Yếu tố bảo vệ</span></div>', unsafe_allow_html=True)
                st.altair_chart(tidy(ch), width="stretch")

# ---------------------------------------------------------------- TAB 3: KHUYẾN NGHỊ & TƯ VẤN LÂM SÀNG
with tab_advice:
    st.markdown('<div class="hello">Khuyến nghị & Tư vấn Sức khỏe Tim mạch</div><div class="sub">Tài liệu hướng dẫn lối sống, chế độ dinh dưỡng và định hướng chăm sóc y tế chuyên sâu.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="card" style="height:100%">
            <h4>🥗 Dinh dưỡng & Lối sống bảo vệ tim</h4>
            <div class="hint">Biện pháp phòng ngừa chủ động hằng ngày</div>
            <ul style="padding-left:18px;line-height:1.8;font-size:14.5px;margin:0">
                <li><b>Kiểm soát muối:</b> Hạn chế lượng natri nạp vào để duy trì ổn định huyết áp tâm thu.</li>
                <li><b>Chất béo có lợi:</b> Tăng cường bổ sung omega-3 từ cá biển, các loại hạt và dầu thực vật.</li>
                <li><b>Vận động thể lực:</b> Duy trì tập luyện thể dục nhịp điệu hoặc đi bộ ít nhất 30 phút mỗi ngày.</li>
                <li><b>Kiểm soát cân nặng:</b> Giữ chỉ số khối cơ thể (BMI) ở mức hợp lý để giảm gánh nặng cho cơ tim.</li>
                <li><b>Nói không với thuốc lá:</b> Tránh xa khói thuốc lá và hạn chế tối đa đồ uống có cồn.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card" style="height:100%">
            <h4>🩺 Định hướng theo dõi y tế</h4>
            <div class="hint">Quy trình chăm sóc và thăm khám định kỳ</div>
            <ul style="padding-left:18px;line-height:1.8;font-size:14.5px;margin:0">
                <li><b>Đo huyết áp định kỳ:</b> Theo dõi huyết áp tại nhà thường xuyên, đặc biệt khi có dấu hiệu mệt mỏi.</li>
                <li><b>Xét nghiệm máu tổng quát:</b> Kiểm tra định kỳ chỉ số đường huyết đói và bộ mỡ máu (Cholesterol, Triglycerid).</li>
                <li><b>Tầm soát chuyên sâu:</b> Thực hiện điện tâm đồ (ECG) hoặc siêu âm tim định kỳ theo lịch hẹn của bác sĩ.</li>
                <li><b>Lắng nghe cơ thể:</b> Chủ động thăm khám ngay khi xuất hiện các triệu chứng đau thắt ngực, khó thở khi gắng sức.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)