"""Hệ thống giao diện y tế: Tông nền xám lam bệnh viện, chữ lớn, tương phản cao, không icon."""

# Bảng màu chuẩn lâm sàng (Clinical Palette)
BG_MEDICAL = "#eaf0f6"      # Nền phòng khám xám lam nhạt
SURFACE_WHITE = "#ffffff"   # Thẻ nội dung màu trắng nổi bật
TEXT_MAIN = "#0a2540"       # Xanh thẫm y tế, độ tương phản cao cho tiêu đề
TEXT_BODY = "#203040"       # Màu chữ nội dung đậm, dễ đọc
BORDER_COLOR = "#b9cddb"    # Viền xanh xám phân định rõ ràng
PRIMARY_BLUE = "#006699"    # Xanh chuẩn y tế cho nút và thanh nhấn

# Màu phân tầng nguy cơ (Nền nhạt, chữ đậm, viền rõ)
LEVEL_STYLE = {
    "Thấp": ("#e6f4ea", "#137333", "#1e8e3e"),
    "Trung bình": ("#fef7e0", "#b06000", "#f9ab00"),
    "Cao": ("#fce8e6", "#c5221f", "#d93025")
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: #eaf0f6 !important;
    color: #203040 !important;
    font-size: 15px !important;
}

header[data-testid="stHeader"], footer, #MainMenu {
    display: none !important;
}

.block-container {
    max-width: 1360px !important;
    padding: 1.5rem 2rem 3rem !important;
}

/* 1. THANH TIÊU ĐỀ ĐẦU TRANG ĐỘC LẬP (KHÔNG CẮT CHỮ) */
.hospital-header {
    background: #ffffff;
    border: 1px solid #b9cddb;
    border-radius: 10px;
    padding: 16px 24px;
    margin-bottom: 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.header-title {
    font-size: 20px;
    font-weight: 800;
    color: #0a2540;
    letter-spacing: -0.01em;
}
.header-desc {
    font-size: 14px;
    color: #4a5d6e;
    font-weight: 500;
    margin-top: 4px;
}
.header-tag {
    background: #dbeafe;
    color: #1e40af;
    border: 1px solid #bfdbfe;
    padding: 6px 14px;
    border-radius: 6px;
    font-size: 13.5px;
    font-weight: 700;
}

/* 2. CỤM TABS ĐIỀU HƯỚNG */
.stTabs [data-baseweb="tab-list"] {
    background: #ffffff;
    padding: 5px;
    border-radius: 8px;
    border: 1px solid #b9cddb;
    gap: 8px;
    margin-bottom: 16px;
}
.stTabs [data-baseweb="tab"] {
    height: 42px;
    border-radius: 6px;
    font-size: 15px;
    font-weight: 700;
    color: #4a5d6e;
    padding: 0 24px;
    border: none !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: #006699 !important;
    color: #ffffff !important;
}

/* 3. KHỐI KẾT QUẢ VÀ SCORECARD */
.score-box {
    background: #ffffff;
    border: 2px solid #b9cddb;
    border-radius: 12px;
    padding: 24px 20px;
    text-align: center;
    margin-bottom: 16px;
}
.score-value {
    font-size: 60px;
    font-weight: 800;
    line-height: 1;
    margin: 8px 0 12px;
}
.risk-badge {
    display: inline-block;
    padding: 6px 18px;
    border-radius: 6px;
    font-size: 15px;
    font-weight: 800;
}

/* 4. THANH CHỈ THỊ NGUY CƠ */
.risk-track {
    position: relative;
    height: 14px;
    border-radius: 99px;
    margin: 20px 0 10px;
    background: linear-gradient(90deg, #1e8e3e 0%, #1e8e3e __LOW__%, #f9ab00 __LOW__%, #f9ab00 __HIGH__%, #d93025 __HIGH__%, #d93025 100%);
}
.risk-pointer {
    position: absolute;
    top: -5px;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: #0a2540;
    border: 3.5px solid #ffffff;
    box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    transform: translateX(-50%);
}
.risk-labels {
    display: flex;
    justify-content: space-between;
    font-size: 13.5px;
    font-weight: 700;
    color: #4a5d6e;
}

/* 5. DÒNG PHÂN TÍCH CHỈ SỐ */
.eval-row {
    background: #f7fafc;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 12px;
}
.eval-hdr {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 15px;
    font-weight: 700;
    color: #0a2540;
}
.eval-text {
    font-size: 14.5px;
    color: #2d3748;
    margin-top: 6px;
    line-height: 1.6;
}

/* 6. NÚT VÀ FORM */
.stButton>button {
    border-radius: 6px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    border: 1px solid #b9cddb !important;
    background: #ffffff !important;
    color: #0a2540 !important;
    padding: 8px 16px !important;
}
.stButton>button:hover {
    border-color: #006699 !important;
    color: #006699 !important;
    background: #f0f7ff !important;
}
.stFormSubmitButton>button {
    background: #006699 !important;
    color: #ffffff !important;
    font-weight: 800 !important;
    height: 50px !important;
    border-radius: 8px !important;
    border: none !important;
    font-size: 16px !important;
}
.stFormSubmitButton>button:hover {
    background: #004d73 !important;
}

/* Thẻ Container chuẩn Streamlit */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border-radius: 10px !important;
    border: 1px solid #b9cddb !important;
    padding: 20px !important;
    margin-bottom: 16px !important;
}

label p {
    font-size: 14.5px !important;
    font-weight: 700 !important;
    color: #0a2540 !important;
}
</style>
"""

def css(low, high):
    return CSS.replace("__LOW__", f"{low*100:.0f}").replace("__HIGH__", f"{high*100:.0f}")

def topbar():
    return """
    <div class="hospital-header">
        <div>
            <div class="header-title">HỆ THỐNG HỖ TRỢ DỰ ĐOÁN NGUY CƠ BỆNH TIM MẠCH</div>
            <div class="header-desc">Cơ sở dữ liệu Viện Tim mạch Cleveland</div>
        </div>
        <div class="header-tag">Mô hình phân loại: Logistic Regression (Recall: 89.7%)</div>
    </div>
    """

def zones(p, low, high):
    mark = f'<div class="risk-pointer" style="left:{min(max(p, 0), 1)*100:.1f}%;"></div>' if p is not None else ""
    return f"""
    <div class="risk-track">{mark}</div>
    <div class="risk-labels">
        <span>Thấp (&lt; {low:.0%})</span>
        <span>Trung bình ({low:.0%} - {high:.0%})</span>
        <span>Cao (≥ {high:.0%})</span>
    </div>
    """