import sys
from datetime import datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT)); sys.path.append(str(Path(__file__).resolve().parent))

import altair as alt
import pandas as pd
import streamlit as st
from src.predict import predict_risk, explain, RULES, LOW, HIGH
import style as S

st.set_page_config(
    page_title="Hệ thống hỗ trợ dự đoán nguy cơ bệnh tim mạch",
    layout="wide"
)

st.markdown(S.css(LOW, HIGH), unsafe_allow_html=True)
st.markdown(S.topbar(), unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv(ROOT / "data" / "heart_clean.csv")

df_clean = load_data()

st.session_state.setdefault("history", [])
st.session_state.setdefault("last", None)

SAMPLES = {
    "low": dict(age=36, sex=0, cp=2, trestbps=115, chol=170, fbs=0, restecg=0, thalach=175, exang=0, oldpeak=0.0, slope=2, ca=0, thal=2),
    "mid": dict(age=55, sex=1, cp=1, trestbps=135, chol=228, fbs=0, restecg=1, thalach=145, exang=0, oldpeak=1.2, slope=1, ca=1, thal=2),
    "high": dict(age=64, sex=1, cp=0, trestbps=158, chol=285, fbs=1, restecg=2, thalach=110, exang=1, oldpeak=3.2, slope=0, ca=2, thal=3),
}

DEFAULT = SAMPLES["mid"]
for k, v in DEFAULT.items():
    st.session_state.setdefault(f"in_{k}", v)

def fill(sample_name):
    for k, v in SAMPLES[sample_name].items():
        st.session_state[f"in_{k}"] = v

tab_pred, tab_benchmark, tab_library = st.tabs([
    "Dự đoán nguy cơ cá nhân",
    "Định vị chỉ số và quần thể",
    "Tài liệu y khoa tham khảo"
])

# ==============================================================================
# TAB 1: DỰ ĐOÁN NGUY CƠ CÁ NHÂN
# ==============================================================================
with tab_pred:
    left, right = st.columns([1.1, 1.25], gap="large")
    
    with left:
        with st.container(border=True):
            st.markdown("<h3 style='margin-top:0;font-size:18px;font-weight:800;color:#0a2540;'>Nhập thông số thăm khám và xét nghiệm</h3>", unsafe_allow_html=True)
            st.markdown("<div style='font-size:14px;color:#4a5d6e;margin-bottom:12px;'>Chọn hồ sơ mẫu để tải nhanh số liệu hoặc nhập trực tiếp:</div>", unsafe_allow_html=True)
            
            b1, b2, b3 = st.columns(3)
            b1.button("Hồ sơ khỏe mạnh", on_click=fill, args=("low",), use_container_width=True)
            b2.button("Tiền lâm sàng", on_click=fill, args=("mid",), use_container_width=True)
            b3.button("Nguy cơ cao", on_click=fill, args=("high",), use_container_width=True)
            
            with st.form("clinical_form"):
                st.markdown("<div style='font-size:13px;font-weight:800;color:#006699;text-transform:uppercase;margin:14px 0 6px;'>1. Nhân khẩu học và huyết động</div>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                age = c1.number_input("Tuổi bệnh nhân", *RULES["age"], key="in_age")
                sex = c2.selectbox("Giới tính", [1, 0], format_func=lambda v: "Nam" if v == 1 else "Nữ", key="in_sex")
                trestbps = c1.number_input("Huyết áp tâm thu lúc nghỉ (mmHg)", *RULES["trestbps"], key="in_trestbps")
                thalach = c2.number_input("Nhịp tim tối đa khi gắng sức (nhịp/phút)", *RULES["thalach"], key="in_thalach")
                
                st.markdown("<div style='font-size:13px;font-weight:800;color:#006699;text-transform:uppercase;margin:14px 0 6px;'>2. Xét nghiệm sinh hóa và điện tâm đồ</div>", unsafe_allow_html=True)
                c3, c4 = st.columns(2)
                chol = c3.number_input("Cholesterol toàn phần (mg/dl)", *RULES["chol"], key="in_chol")
                fbs = c4.selectbox("Đường huyết lúc đói", [0, 1], format_func=lambda v: "Bình thường (≤ 120 mg/dl)" if v == 0 else "Cao (> 120 mg/dl)", key="in_fbs")
                restecg = st.selectbox("Điện tâm đồ lúc nghỉ (ECG)", [0, 1, 2],
                                       format_func=lambda v: {0: "Bình thường", 1: "Bất thường sóng ST-T", 2: "Phì đại thất trái"}[v], key="in_restecg")
                
                st.markdown("<div style='font-size:13px;font-weight:800;color:#006699;text-transform:uppercase;margin:14px 0 6px;'>3. Triệu chứng lâm sàng và gắng sức</div>", unsafe_allow_html=True)
                cp = st.selectbox("Dạng đau ngực", [0, 1, 2, 3], format_func=lambda v: {
                    0: "Đau thắt ngực điển hình (tức ngực khi gắng sức)",
                    1: "Đau thắt ngực không điển hình (thoáng qua)",
                    2: "Đau ngực không do nguyên nhân tim",
                    3: "Không có triệu chứng đau ngực"
                }[v], key="in_cp")
                
                c5, c6 = st.columns(2)
                exang = c5.selectbox("Đau thắt ngực khi gắng sức", [0, 1], format_func=lambda v: "Không có" if v == 0 else "Có xuất hiện", key="in_exang")
                slope = c6.selectbox("Độ dốc đoạn ST gắng sức", [0, 1, 2], format_func=lambda v: {0: "Dốc lên", 1: "Đi ngang (bằng phẳng)", 2: "Dốc xuống"}[v], key="in_slope")
                
                c7, c8 = st.columns(2)
                oldpeak = c7.number_input("Độ chênh xuống đoạn ST (mm)", 0.0, 7.0, step=0.1, key="in_oldpeak")
                ca = c8.selectbox("Số nhánh mạch vành bị hẹp (0-3)", [0, 1, 2, 3], key="in_ca")
                thal = st.selectbox("Xạ hình tưới máu cơ tim (Thal)", [1, 2, 3], format_func=lambda v: {1: "Tưới máu bình thường", 2: "Khuyết tật cố định (sẹo hoại tử)", 3: "Khuyết tật hồi phục (thiếu máu cục bộ)"}[v], key="in_thal")
                
                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                submit = st.form_submit_button("Thực hiện phân tích và đánh giá nguy cơ", use_container_width=True)
                
            if submit:
                payload = dict(age=age, sex=sex, cp=cp, trestbps=trestbps, chol=chol, fbs=fbs, restecg=restecg,
                               thalach=thalach, exang=exang, oldpeak=oldpeak, slope=slope, ca=ca, thal=thal)
                try:
                    p, lv = predict_risk(payload)
                    st.session_state.last = dict(p=p, level=lv, ex=explain(payload), inputs=payload)
                    st.session_state.history.append(dict(
                        time=datetime.now().strftime("%H:%M:%S"),
                        who=f"{'Nam' if sex == 1 else 'Nữ'}, {int(age)} tuổi",
                        p=p, level=lv, inputs=payload
                    ))
                except Exception as e:
                    st.session_state.last = dict(error=str(e))

    with right:
        last = st.session_state.last
        if last is None:
            with st.container(border=True):
                st.markdown("""
                <div style="text-align:center;padding:80px 20px;">
                    <div style="font-size:20px;font-weight:800;color:#0a2540;">Hệ thống sẵn sàng đánh giá</div>
                    <div style="font-size:15px;color:#4a5d6e;max-width:400px;margin:10px auto 0;line-height:1.6;">
                        Vui lòng nhập các thông số thăm khám bên trái hoặc chọn nhanh hồ sơ mẫu, sau đó nhấn nút thực hiện phân tích để xem kết quả.
                    </div>
                </div>
                """, unsafe_allow_html=True)
        elif "error" in last:
            st.error(f"Lỗi: {last['error']}")
        else:
            p, lv = last["p"], last["level"]
            inp = last["inputs"]
            bg, fg, dot = S.LEVEL_STYLE[lv]
            
           # Khối kết quả đánh giá nguy cơ (đã triệt tiêu lỗi thụt lề khoảng trắng)
            st.markdown(
                f'<div class="score-box" style="border-color:{dot};">'
                f'<div style="font-size:14px;font-weight:800;color:#4a5d6e;text-transform:uppercase;letter-spacing:0.04em;">Xác suất nguy cơ mắc bệnh tim mạch</div>'
                f'<div class="score-value" style="color:{fg};">{p*100:.1f}%</div>'
                f'<div class="risk-badge" style="background:{bg};color:{fg};border:1.5px solid {dot};">Phân tầng lâm sàng: Mức độ {lv.lower()}</div>'
                f'{S.zones(p, LOW, HIGH).strip()}'
                f'</div>',
                unsafe_allow_html=True
            )
            # Phân tích chi tiết chỉ số
            with st.container(border=True):
                st.markdown("<h3 style='margin-top:0;font-size:17px;font-weight:800;color:#0a2540;'>Phân tích chi tiết các chỉ số lâm sàng và sinh hóa</h3>", unsafe_allow_html=True)
                st.markdown("<div style='font-size:13.5px;color:#4a5d6e;margin-bottom:14px;'>Đối chiếu theo chuẩn Hội Tim mạch học Việt Nam (VNHA) và AHA:</div>", unsafe_allow_html=True)
                
                # 1. Huyết động
                bp = inp['trestbps']
                hr_max_theory = 220 - inp['age']
                hr_pct = (inp['thalach'] / hr_max_theory) * 100
                bp_eval = ("Tối ưu", "#137333", "#e6f4ea", "Áp lực nội mạch trong giới hạn ổn định.") if bp < 120 else (
                    ("Tiền tăng huyết áp", "#b06000", "#fef7e0", "Huyết áp ở ngưỡng cảnh báo (120-139 mmHg), cần điều chỉnh lượng muối ăn vào.") if bp <= 139 else
                    ("Tăng huyết áp", "#c5221f", "#fce8e6", "Vượt 140 mmHg, làm tăng gánh nặng co bóp cho thất trái và tổn thương mạch máu.")
                )
                
                # 2. Sinh hóa
                cl = inp['chol']
                cl_eval = ("Lý tưởng", "#137333", "#e6f4ea", "Nồng độ mỡ máu trong giới hạn bình thường (< 200 mg/dl).") if cl < 200 else (
                    ("Ranh giới cao", "#b06000", "#fef7e0", "Ngưỡng 200-239 mg/dl bắt đầu làm tăng nguy cơ lắng đọng mảng xơ vữa.") if cl <= 239 else
                    ("Tăng cholesterol máu", "#c5221f", "#fce8e6", "Chỉ số > 240 mg/dl là tác nhân trực tiếp gây xơ vữa và tắc hẹp mạch vành.")
                )
                
                # 3. Gắng sức & ECG
                st_eval = ("Bình thường", "#137333", "#e6f4ea", "Không ghi nhận đoạn ST chênh xuống khi gắng sức.") if inp['oldpeak'] < 1.0 else (
                    ("Nghi ngờ thiếu máu", "#b06000", "#fef7e0", f"ST chênh {inp['oldpeak']} mm, phản ánh dấu hiệu thiếu máu cơ tim.") if inp['oldpeak'] <= 2.0 else
                    ("Thiếu máu cơ tim rõ rệt", "#c5221f", "#fce8e6", f"ST chênh {inp['oldpeak']} mm, cảnh báo nguy cơ thiếu máu cơ tim diện rộng.")
                )
                
                st.markdown(f"""
                <div class="eval-row">
                    <div class="eval-hdr">
                        <span>1. Hệ huyết động: Huyết áp ({bp} mmHg) và nhịp tim tối đa ({int(inp['thalach'])} nhịp/phút)</span>
                        <span style="background:{bp_eval[2]};color:{bp_eval[1]};padding:3px 10px;border-radius:4px;font-size:13px;white-space:nowrap;">{bp_eval[0]}</span>
                    </div>
                    <div class="eval-text">{bp_eval[3]} Nhịp tim gắng sức đạt <b>{hr_pct:.1f}%</b> so với tần số tim tối đa lý thuyết theo tuổi (220 - tuổi = {hr_max_theory} nhịp/phút).</div>
                </div>
                
                <div class="eval-row">
                    <div class="eval-hdr">
                        <span>2. Bộ mỡ máu: Cholesterol toàn phần ({cl} mg/dl)</span>
                        <span style="background:{cl_eval[2]};color:{cl_eval[1]};padding:3px 10px;border-radius:4px;font-size:13px;white-space:nowrap;">{cl_eval[0]}</span>
                    </div>
                    <div class="eval-text">{cl_eval[3]}</div>
                </div>
                
                <div class="eval-row">
                    <div class="eval-hdr">
                        <span>3. Điện tâm đồ và đáp ứng gắng sức: ST chênh ({inp['oldpeak']} mm)</span>
                        <span style="background:{st_eval[2]};color:{st_eval[1]};padding:3px 10px;border-radius:4px;font-size:13px;white-space:nowrap;">{st_eval[0]}</span>
                    </div>
                    <div class="eval-text">{st_eval[3]} Dạng độ dốc đoạn ST: <b>{['Dốc lên', 'Đi ngang', 'Dốc xuống'][int(inp['slope'])]}</b>.</div>
                </div>
                
                <div class="eval-row">
                    <div class="eval-hdr">
                        <span>4. Đánh giá mạch vành: {int(inp['ca'])} nhánh mạch chính bị hẹp</span>
                        <span style="background:{'#e6f4ea' if inp['ca']==0 else '#fce8e6'};color:{'#137333' if inp['ca']==0 else '#c5221f'};padding:3px 10px;border-radius:4px;font-size:13px;white-space:nowrap;">{'Bình thường' if inp['ca']==0 else 'Phát hiện hẹp mạch vành'}</span>
                    </div>
                    <div class="eval-text">Số nhánh mạch vành chính bị cản quang là <b>{int(inp['ca'])}/3</b> nhánh. Kết quả xạ hình tưới máu: <b>{['Bình thường', 'Khuyết tật cố định', 'Khuyết tật hồi phục'][int(inp['thal'])-1]}</b>.</div>
                </div>
                """, unsafe_allow_html=True)

            # Biểu đồ đóng góp yếu tố
            with st.container(border=True):
                st.markdown("<h3 style='margin-top:0;font-size:17px;font-weight:800;color:#0a2540;'>Trọng số đóng góp vào kết quả đánh giá (Linear SHAP)</h3>", unsafe_allow_html=True)
                st.markdown("<div style='font-size:13.5px;color:#4a5d6e;margin-bottom:10px;'>Mức độ tác động làm tăng hoặc giảm xác suất nguy cơ của từng chỉ số:</div>", unsafe_allow_html=True)
                
                ex_df = last["ex"].head(6).reset_index()
                ex_df.columns = ["Chỉ số", "Trọng số"]
                ex_df["Tác động"] = ex_df["Trọng số"].apply(lambda v: "Tăng nguy cơ" if v > 0 else "Giảm nguy cơ")
                
                ch = alt.Chart(ex_df).mark_bar(cornerRadiusEnd=4, height=20).encode(
                    y=alt.Y("Chỉ số:N", sort=None, axis=alt.Axis(title=None, labelFontSize=13)),
                    x=alt.X("Trọng số:Q", title="Mức độ tác động (Log-odds)", axis=alt.Axis(labelFontSize=12, titleFontSize=13)),
                    color=alt.Color("Tác động:N", scale=alt.Scale(domain=["Tăng nguy cơ", "Giảm nguy cơ"], range=["#d93025", "#1e8e3e"]), legend=alt.Legend(orient="bottom", title=None, labelFontSize=13)),
                    tooltip=["Chỉ số", alt.Tooltip("Trọng số:Q", format=".2f"), "Tác động"]
                ).properties(height=200)
                st.altair_chart(ch, use_container_width=True)

            # Hướng dẫn và khuyến nghị
            with st.container(border=True):
                st.markdown("<h3 style='margin-top:0;font-size:17px;font-weight:800;color:#0a2540;'>Khuyến nghị can thiệp và theo dõi</h3>", unsafe_allow_html=True)
                c_act1, c_act2 = st.columns(2)
                with c_act1:
                    st.markdown("""
                    <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:16px;font-size:14.5px;line-height:1.7;color:#166534;">
                        <b>Chế độ dinh dưỡng và dự phòng:</b><br>
                        • Áp dụng chế độ ăn giàu rau xanh, các loại hạt và cá béo chứa nhiều Omega-3.<br>
                        • Duy trì đi bộ hoặc tập thể dục vừa sức 30 phút mỗi ngày, 5 ngày mỗi tuần.<br>
                        • Theo dõi và ghi chép huyết áp tại nhà 2 lần mỗi ngày (sáng và chiều tối).<br>
                        • Duy trì chỉ số khối cơ thể (BMI) ở mức hợp lý từ 18.5 đến 22.9.
                    </div>
                    """, unsafe_allow_html=True)
                with c_act2:
                    st.markdown("""
                    <div style="background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:16px;font-size:14.5px;line-height:1.7;color:#991b1b;">
                        <b>Cảnh báo và hướng dẫn y tế:</b><br>
                        • Hạn chế lượng muối ăn dưới 5g mỗi ngày, giảm tối đa mỡ động vật và đồ chiên xào.<br>
                        • Ngừng sử dụng thuốc lá, tránh xa bia rượu và các chất kích thích tim mạch.<br>
                        • Khám chuyên khoa tim mạch định kỳ để làm siêu âm tim và đo điện tâm đồ gắng sức.<br>
                        • Đến ngay cơ sở y tế gần nhất nếu có cơn đau thắt ngực lan ra vai hoặc kéo dài trên 15 phút.
                    </div>
                    """, unsafe_allow_html=True)

# ==============================================================================
# TAB 2: ĐỊNH VỊ CHỈ SỐ VÀ QUẦN THỂ
# ==============================================================================
with tab_benchmark:
    with st.container(border=True):
        st.markdown("<h3 style='margin-top:0;font-size:18px;font-weight:800;color:#0a2540;'>Định vị chỉ số sức khỏe so với quần thể dữ liệu lâm sàng</h3>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:14px;color:#4a5d6e;margin-bottom:14px;'>So sánh trực tiếp các chỉ số của bạn với phân bố của 302 ca bệnh án tại Viện Tim mạch Cleveland:</div>", unsafe_allow_html=True)
        
        hist = st.session_state.history
        cur_inp = st.session_state.last["inputs"] if st.session_state.last else DEFAULT
        cur_p = st.session_state.last["p"] if st.session_state.last else 0.412
        
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Lần tầm soát", f"{len(hist)} lượt", "Trong phiên làm việc")
        k2.metric("Xác suất hiện tại", f"{cur_p*100:.1f}%", f"Mức {st.session_state.last['level'] if st.session_state.last else 'Mặc định'}")
        k3.metric("Phân vị huyết áp", f"Mức {int((df_clean['trestbps'] < cur_inp['trestbps']).mean()*100)}%", "So với quần thể bệnh nhân")
        k4.metric("Phân vị mỡ máu", f"Mức {int((df_clean['chol'] < cur_inp['chol']).mean()*100)}%", "So với quần thể bệnh nhân")

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    
    col_bench1, col_bench2 = st.columns(2, gap="large")
    
    with col_bench1:
        with st.container(border=True):
            st.markdown("<h4 style='margin-top:0;font-size:16px;font-weight:800;color:#0a2540;'>1. Vị trí huyết áp tâm thu trên phân bố quần thể</h4>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:13.5px;color:#4a5d6e;margin-bottom:8px;'>Huyết áp của bạn: <b>{cur_inp['trestbps']} mmHg</b> (vạch chỉ thị màu đỏ):</div>", unsafe_allow_html=True)
            
            hist_bp = alt.Chart(df_clean).mark_bar(opacity=0.65, color="#006699").encode(
                x=alt.X("trestbps:Q", bin=alt.Bin(maxbins=25), title="Huyết áp tâm thu (mmHg)", axis=alt.Axis(labelFontSize=12, titleFontSize=13)),
                y=alt.Y("count()", title="Số bệnh nhân", axis=alt.Axis(labelFontSize=12, titleFontSize=13)),
                tooltip=["count()"]
            )
            rule_bp = alt.Chart(pd.DataFrame({'x': [cur_inp['trestbps']]})).mark_rule(color="#d93025", strokeWidth=3).encode(x='x:Q')
            st.altair_chart((hist_bp + rule_bp).properties(height=240), use_container_width=True)
            
        with st.container(border=True):
            st.markdown("<h4 style='margin-top:0;font-size:16px;font-weight:800;color:#0a2540;'>3. Tương quan độ tuổi và nhịp tim tối đa</h4>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:13.5px;color:#4a5d6e;margin-bottom:8px;'>Vị trí của bạn: <b>{int(cur_inp['age'])} tuổi</b>, <b>{int(cur_inp['thalach'])} nhịp/phút</b> (điểm tròn cam lớn):</div>", unsafe_allow_html=True)
            
            scatter_base = alt.Chart(df_clean).mark_circle(size=60, opacity=0.45).encode(
                x=alt.X("age:Q", title="Tuổi", axis=alt.Axis(labelFontSize=12, titleFontSize=13)),
                y=alt.Y("thalach:Q", title="Nhịp tim tối đa khi gắng sức (nhịp/phút)", axis=alt.Axis(labelFontSize=12, titleFontSize=13)),
                color=alt.Color("HeartDisease:N", scale=alt.Scale(domain=[0, 1], range=["#1e8e3e", "#d93025"]), legend=alt.Legend(title="Trạng thái", orient="bottom", labelFontSize=12)),
                tooltip=["age", "thalach"]
            )
            my_point = alt.Chart(pd.DataFrame({'age': [cur_inp['age']], 'thalach': [cur_inp['thalach']]})).mark_circle(size=200, color="#f9ab00").encode(
                x='age:Q', y='thalach:Q'
            )
            st.altair_chart((scatter_base + my_point).properties(height=240), use_container_width=True)

    with col_bench2:
        with st.container(border=True):
            st.markdown("<h4 style='margin-top:0;font-size:16px;font-weight:800;color:#0a2540;'>2. Vị trí cholesterol toàn phần trên phân bố quần thể</h4>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:13.5px;color:#4a5d6e;margin-bottom:8px;'>Cholesterol của bạn: <b>{cur_inp['chol']} mg/dl</b> (vạch chỉ thị màu đỏ):</div>", unsafe_allow_html=True)
            
            hist_cl = alt.Chart(df_clean).mark_bar(opacity=0.65, color="#008080").encode(
                x=alt.X("chol:Q", bin=alt.Bin(maxbins=25), title="Cholesterol toàn phần (mg/dl)", axis=alt.Axis(labelFontSize=12, titleFontSize=13)),
                y=alt.Y("count()", title="Số bệnh nhân", axis=alt.Axis(labelFontSize=12, titleFontSize=13)),
                tooltip=["count()"]
            )
            rule_cl = alt.Chart(pd.DataFrame({'x': [cur_inp['chol']]})).mark_rule(color="#d93025", strokeWidth=3).encode(x='x:Q')
            st.altair_chart((hist_cl + rule_cl).properties(height=240), use_container_width=True)

        with st.container(border=True):
            st.markdown("<h4 style='margin-top:0;font-size:16px;font-weight:800;color:#0a2540;'>4. Lịch sử các lần đánh giá trong phiên làm việc</h4>", unsafe_allow_html=True)
            if hist:
                hist_table = pd.DataFrame([
                    {"Thời gian": h["time"], "Hồ sơ": h["who"], "Xác suất": f"{h['p']*100:.1f}%", "Mức nguy cơ": h["level"]}
                    for h in reversed(hist)
                ])
                st.dataframe(hist_table, hide_index=True, use_container_width=True, height=240)
            else:
                st.info("Chưa có lịch sử đánh giá trong phiên này. Hãy thực hiện ít nhất một lần phân tích tại tab đầu tiên.")

# ==============================================================================
# TAB 3: TÀI LIỆU Y KHOA THAM KHẢO (21 TÀI LIỆU CHÍNH THỐNG)
# ==============================================================================
with tab_library:
    with st.container(border=True):
        st.markdown("<h3 style='margin-top:0;font-size:18px;font-weight:800;color:#0a2540;'>Tài liệu y khoa và hướng dẫn lâm sàng chính thống</h3>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:14px;color:#4a5d6e;margin-bottom:16px;'>Tổng hợp 21 tài liệu hướng dẫn điều trị, khuyến cáo chẩn đoán và nghiên cứu khoa học từ các tổ chức chuyên môn:</div>", unsafe_allow_html=True)
        
        c_cat1, c_cat2 = st.columns(2, gap="large")
        
        with c_cat1:
            st.markdown("<h4 style='font-size:16px;font-weight:800;color:#006699;margin-bottom:10px;'>Hướng dẫn lâm sàng tim mạch Việt Nam (VNHA và Bộ Y tế)</h4>", unsafe_allow_html=True)
            docs_vn = [
                ("Khuyến cáo về chẩn đoán và điều trị tăng huyết áp", "Hội Tim mạch học Việt Nam (VNHA 2022) - Phân loại tăng huyết áp và phác đồ điều trị.", "https://vnha.org.vn/"),
                ("Hướng dẫn chẩn đoán và xử trí hội chứng vành cấp", "Bộ Y tế Việt Nam (Quyết định 2187/QĐ-BYT) - Quy trình cấp cứu và can thiệp mạch vành.", "https://kcb.vn/"),
                ("Khuyến cáo xử trí rối loạn lipid máu", "Hội Tim mạch học Việt Nam (VNHA 2020) - Kiểm soát nồng độ LDL-C theo phân tầng nguy cơ.", "https://vnha.org.vn/"),
                ("Hướng dẫn dự phòng tiên phát bệnh tim mạch", "Phân hội Xơ vữa Động mạch Việt Nam - Đánh giá và kiểm soát yếu tố nguy cơ từ sớm.", "https://vnha.org.vn/"),
                ("Khuyến cáo chẩn đoán và quản lý bệnh tim thiếu máu cục bộ mãn", "Hội Tim mạch học Việt Nam - Tiêu chuẩn chỉ định điện tâm đồ và chụp mạch vành.", "https://vnha.org.vn/"),
                ("Hướng dẫn dự phòng đột quỵ và bệnh mạch não", "Hội Đột quỵ Việt Nam - Mối liên hệ giữa tổn thương mạch máu và nguy cơ tai biến.", "https://dotquy.vn/")
            ]
            for title, desc, url in docs_vn:
                st.markdown(f"""
                <div style="background:#f7fafc;border:1px solid #cbd5e1;border-left:4px solid #006699;border-radius:6px;padding:12px 16px;margin-bottom:10px;">
                    <div style="font-weight:700;font-size:14.5px;color:#0a2540;">{title}</div>
                    <div style="font-size:13.5px;color:#4a5d6e;margin:4px 0 6px;">{desc}</div>
                    <a href="{url}" target="_blank" style="font-size:13px;font-weight:700;color:#006699;text-decoration:none;">Xem tài liệu gốc</a>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("<h4 style='font-size:16px;font-weight:800;color:#006699;margin:16px 0 10px;'>Tổ chức Y tế Thế giới (WHO) và nghiên cứu dịch tễ</h4>", unsafe_allow_html=True)
            docs_who = [
                ("Gói can thiệp thiết yếu về bệnh không lây nhiễm (WHO PEN)", "Quy trình phát hiện và quản lý bệnh tim mạch tại trạm y tế cơ sở của WHO.", "https://www.who.int/publications/i/item/9789241511452"),
                ("Báo cáo toàn cầu về kiểm soát tăng huyết áp (WHO 2023)", "Số liệu dịch tễ học và khuyến cáo giảm lượng muối natri trong chế độ ăn hàng ngày.", "https://www.who.int/publications/i/item/9789240081062"),
                ("Nghiên cứu thuật toán chẩn đoán bệnh động mạch vành (Detrano và cộng sự, 1989)", "Công trình nghiên cứu ứng dụng dữ liệu lâm sàng Cleveland được trích dẫn trong đề tài.", "https://pubmed.ncbi.nlm.nih.gov/2712249/"),
                ("Nghiên cứu tim mạch Framingham (Framingham Heart Study)", "Cơ sở dữ liệu đặt nền móng cho các thang điểm ước tính nguy cơ tim mạch toàn cầu.", "https://www.framinghamheartstudy.org/"),
                ("Báo cáo gánh nặng bệnh tim mạch toàn cầu (The Lancet GBD Study)", "Thống kê dịch tễ học và các yếu tố nguy cơ tim mạch hàng đầu trên thế giới.", "https://www.thelancet.com/")
            ]
            for title, desc, url in docs_who:
                st.markdown(f"""
                <div style="background:#f7fafc;border:1px solid #cbd5e1;border-left:4px solid #008080;border-radius:6px;padding:12px 16px;margin-bottom:10px;">
                    <div style="font-weight:700;font-size:14.5px;color:#0a2540;">{title}</div>
                    <div style="font-size:13.5px;color:#4a5d6e;margin:4px 0 6px;">{desc}</div>
                    <a href="{url}" target="_blank" style="font-size:13px;font-weight:700;color:#008080;text-decoration:none;">Xem tài liệu gốc</a>
                </div>
                """, unsafe_allow_html=True)

        with c_cat2:
            st.markdown("<h4 style='font-size:16px;font-weight:800;color:#006699;margin-bottom:10px;'>Hướng dẫn lâm sàng Hoa Kỳ (ACC, AHA, ADA)</h4>", unsafe_allow_html=True)
            docs_us = [
                ("Hướng dẫn dự phòng tiên phát bệnh tim mạch (AHA/ACC 2019)", "Khuyến cáo về dinh dưỡng, hoạt động thể lực và kiểm soát các chỉ số sinh hóa.", "https://www.ahajournals.org/doi/10.1161/CIR.0000000000000678"),
                ("Hướng dẫn quản lý nồng độ cholesterol máu (ACC/AHA 2018)", "Phân tầng nguy cơ xơ vữa động mạch và phác đồ can thiệp nhóm thuốc kiểm soát mỡ máu.", "https://www.ahajournals.org/doi/10.1161/CIR.0000000000000625"),
                ("Hướng dẫn đánh giá và chẩn đoán đau ngực (ACC/AHA 2021)", "Phân loại cơn đau ngực và lưu đồ thực hiện các xét nghiệm gắng sức không xâm lấn.", "https://www.ahajournals.org/doi/10.1161/CIR.0000000000001029"),
                ("Cập nhật số liệu thống kê bệnh tim mạch và đột quỵ (AHA 2024)", "Báo cáo thường niên cập nhật tỷ lệ mắc và can thiệp mạch vành tại Hoa Kỳ.", "https://www.ahajournals.org/"),
                ("Tiêu chuẩn chăm sóc y tế trong đái tháo đường (ADA 2024)", "Kiểm soát đường huyết để giảm biến chứng tim mạch và suy thận mạn.", "https://diabetesjournals.org/care")
            ]
            for title, desc, url in docs_us:
                st.markdown(f"""
                <div style="background:#f7fafc;border:1px solid #cbd5e1;border-left:4px solid #b06000;border-radius:6px;padding:12px 16px;margin-bottom:10px;">
                    <div style="font-weight:700;font-size:14.5px;color:#0a2540;">{title}</div>
                    <div style="font-size:13.5px;color:#4a5d6e;margin:4px 0 6px;">{desc}</div>
                    <a href="{url}" target="_blank" style="font-size:13px;font-weight:700;color:#b06000;text-decoration:none;">Xem tài liệu gốc</a>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<h4 style='font-size:16px;font-weight:800;color:#006699;margin:16px 0 10px;'>Hướng dẫn Châu Âu (ESC) và nghiên cứu trí tuệ nhân tạo</h4>", unsafe_allow_html=True)
            docs_esc = [
                ("Hướng dẫn thực hành dự phòng bệnh tim mạch (ESC 2021)", "Tiêu chuẩn lâm sàng của Hội Tim mạch Châu Âu về can thiệp yếu tố nguy cơ lối sống.", "https://www.escardio.org/Guidelines/Clinical-Practice-Guidelines/Cardiovascular-Disease-Prevention"),
                ("Hướng dẫn quản lý hội chứng vành cấp (ESC 2023)", "Phác đồ theo dõi men tim Troponin và các dạng biến đổi sóng điện tâm đồ ST.", "https://www.escardio.org/"),
                ("Hướng dẫn chẩn đoán và điều trị rối loạn lipid máu (ESC/EAS)", "Mục tiêu kiểm soát mỡ máu ở bệnh nhân có nguy cơ tim mạch rất cao.", "https://www.escardio.org/"),
                ("Nghiên cứu ứng dụng học máy trong tim mạch (Nature Medicine)", "Đánh giá vai trò của các thuật toán phân loại trong chẩn đoán sớm bệnh lý tuần hoàn.", "https://www.nature.com/articles/s41591-020-0942-0"),
                ("Tuyên bố khoa học về trí tuệ nhân tạo trong y học tim mạch (AHA)", "Yêu cầu về tính minh bạch và khả năng giải thích được (XAI) của các mô hình học máy.", "https://www.ahajournals.org/")
            ]
            for title, desc, url in docs_esc:
                st.markdown(f"""
                <div style="background:#f7fafc;border:1px solid #cbd5e1;border-left:4px solid #4a5568;border-radius:6px;padding:12px 16px;margin-bottom:10px;">
                    <div style="font-weight:700;font-size:14.5px;color:#0a2540;">{title}</div>
                    <div style="font-size:13.5px;color:#4a5d6e;margin:4px 0 6px;">{desc}</div>
                    <a href="{url}" target="_blank" style="font-size:13px;font-weight:700;color:#4a5568;text-decoration:none;">Xem tài liệu gốc</a>
                </div>
                """, unsafe_allow_html=True)