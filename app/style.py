"""Giao diện: bảng màu, CSS và các thành phần HTML dùng chung (phong cách dashboard trắng - cam - đen)."""
ORANGE, ORANGE_D, INK, MUTED, BG, LINE = "#e8603c", "#d94d28", "#1b1b1b", "#6b6b6b", "#ececec", "#e6e6e6"
LEVEL_STYLE = {"Thấp": ("#e6f6ee", "#1b8a55", "#2eae6d"), "Trung bình": ("#fff3df", "#a86400", "#f0a53a"), "Cao": ("#fdeae6", "#c4301a", "#e5482b")}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stApp { font-family: 'Inter', 'Segoe UI', Arial, sans-serif; }
.stApp { background: __BG__; }
header[data-testid="stHeader"] { background: transparent; height: 0; }
#MainMenu, footer, [data-testid="stDecoration"] { display: none; }
.block-container { max-width: 1240px; padding: 28px 36px 40px; background: #f7f7f7; border-radius: 32px; margin-top: 24px; margin-bottom: 24px; }
h1, h2, h3 { color: __INK__; letter-spacing: -0.02em; }

/* thanh trên cùng */
.topbar { display:flex; align-items:center; justify-content:space-between; margin-bottom:6px; }
.brand { display:flex; align-items:center; gap:10px; background:#fff; border-radius:999px; padding:8px 18px 8px 10px; font-weight:700; font-size:18px; }
.brand .logo { width:34px; height:34px; border-radius:50%; background:linear-gradient(135deg,#f58a55,__ORANGE_D__); display:flex; align-items:center; justify-content:center; }
.chip { background:#fff; border-radius:999px; padding:9px 16px; font-size:13px; color:__MUTED__; }
.chip b { color:__INK__; }

/* tab = thanh điều hướng dạng viên thuốc (hỗ trợ cả DOM baseweb và react-aria) */
[role="tablist"] { gap:4px; background:#fff; padding:6px; border-radius:999px; width:fit-content; margin:-50px auto 18px; border-bottom:none !important; box-shadow:none !important; }
[data-testid="stTabs"] [data-orientation="horizontal"] { border-bottom:none !important; box-shadow:none !important; }
[data-testid="stTabs"] [data-orientation="horizontal"]::after, [data-testid="stTabs"] [data-orientation="horizontal"]::before { display:none !important; }
[role="tab"] { height:40px; padding:0 22px; border-radius:999px; background:transparent !important; color:__MUTED__; font-weight:500; border:none !important; }
[role="tab"] p { color:inherit !important; font-size:15px; margin:0; }
[role="tab"][aria-selected="true"] { background:__INK__ !important; color:#fff !important; }
[role="tab"][aria-selected="true"] p { color:#fff !important; }
.react-aria-SelectionIndicator, [data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display:none !important; }

.hello { font-size:42px; font-weight:700; line-height:1.1; margin:14px 0 4px; letter-spacing:-0.03em; }
.sub { color:__MUTED__; font-size:15px; margin-bottom:22px; }

/* thẻ */
.card, .st-key-card_form, .st-key-card_result, .st-key-card_sample, .st-key-card_chart { background:#fff; border:1px solid #efefef; border-radius:24px; padding:24px 26px; }
.card h4 { margin:0 0 4px; font-size:19px; font-weight:600; }
.hint { color:__MUTED__; font-size:13.5px; margin-bottom:12px; }
.stat { border-radius:22px; padding:20px 22px; background:#f1f1f1; height:100%; }
.stat .lbl { font-size:14.5px; color:__MUTED__; }
.stat .num { font-size:38px; font-weight:700; letter-spacing:-0.03em; margin:18px 0 12px; line-height:1; }
.stat .foot { font-size:12.5px; color:__MUTED__; }
.stat.hot { background:linear-gradient(160deg,#f58a55,__ORANGE_D__); color:#fff; }
.stat.hot .lbl, .stat.hot .foot { color:rgba(255,255,255,.85); }
.badge { display:inline-block; padding:3px 9px; border-radius:999px; font-size:12px; font-weight:600; margin-right:6px; }
.pill { display:inline-flex; align-items:center; gap:7px; font-size:13.5px; font-weight:500; }
.pill i { width:8px; height:8px; border-radius:50%; display:inline-block; }
.legend { display:flex; gap:16px; font-size:12.5px; color:__MUTED__; margin-bottom:6px; }
.legend span::before { content:''; display:inline-block; width:9px; height:9px; border-radius:3px; margin-right:6px; background:var(--c); }

/* thanh ngưỡng */
.zones { position:relative; height:12px; border-radius:99px; margin:14px 0 8px; background:linear-gradient(90deg,#2eae6d 0 __LOW__%,#f0a53a __LOW__% __HIGH__%,#e5482b __HIGH__% 100%); }
.zones .mark { position:absolute; top:-5px; width:22px; height:22px; border-radius:50%; background:__INK__; border:4px solid #fff; box-shadow:0 1px 4px rgba(0,0,0,.3); transform:translateX(-50%); }
.zlab { display:flex; justify-content:space-between; font-size:12px; color:__MUTED__; }

/* bảng */
table.tbl { width:100%; border-collapse:collapse; font-size:14px; }
table.tbl th { text-align:left; font-weight:500; color:__MUTED__; background:#f3f3f3; padding:12px 14px; }
table.tbl th:first-child { border-radius:12px 0 0 12px; } table.tbl th:last-child { border-radius:0 12px 12px 0; }
table.tbl td { padding:14px; border-bottom:1px solid #f0f0f0; }
.empty { text-align:center; color:__MUTED__; padding:28px 0; font-size:14px; }

/* nút */
.stButton > button, .stFormSubmitButton > button { border-radius:999px; font-weight:600; padding:10px 22px; border:1px solid #d9d9d9; background:#fff; color:__INK__; }
[data-testid="stFormSubmitButton"], [data-testid="stFormSubmitButton"] > button { width:100% !important; }
.stFormSubmitButton > button { background:__INK__; color:#fff; border:none; width:100%; height:48px; font-size:16px; }
.stFormSubmitButton > button:hover { background:#333; color:#fff; }
.stButton > button:hover { border-color:__ORANGE__; color:__ORANGE_D__; }

/* ô nhập */
[data-baseweb="input"], [data-baseweb="select"] > div { border-radius:14px !important; background:#f5f5f5 !important; border-color:transparent !important; }
label p { font-size:13px !important; color:__MUTED__ !important; font-weight:500; }
[data-testid="stForm"] { border:none; padding:0; }
.section-lbl { font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:__ORANGE_D__; font-weight:700; margin:10px 0 2px; }
.note { font-size:12.5px; color:__MUTED__; line-height:1.5; margin-top:12px; }
</style>
"""

def css(low, high):
    s = CSS
    for k, v in {"__BG__": BG, "__INK__": INK, "__MUTED__": MUTED, "__ORANGE__": ORANGE, "__ORANGE_D__": ORANGE_D, "__LOW__": f"{low*100:.0f}", "__HIGH__": f"{high*100:.0f}"}.items():
        s = s.replace(k, v)
    return s

HEART = '<svg width="18" height="18" viewBox="0 0 24 24" fill="#fff"><path d="M12 21s-7.5-4.6-9.6-9.2C.9 8.4 2.7 5 6 5c2 0 3.4 1.1 4 2.2h4C14.6 6.1 16 5 18 5c3.3 0 5.1 3.4 3.6 6.8C19.5 16.4 12 21 12 21z"/></svg>'

def topbar():
    return f'<div class="topbar"><div class="brand"><span class="logo">{HEART}</span>CardioCheck</div><div class="chip"><b>Công cụ học tập</b> · không thay thế chẩn đoán của bác sĩ</div></div>'

def level_pill(level):
    bg, fg, dot = LEVEL_STYLE[level]
    return f'<span class="pill" style="color:{fg}"><i style="background:{dot}"></i>{level}</span>'

def zones(p, low, high):
    mark = f'<div class="mark" style="left:{min(max(p,0),1)*100:.1f}%"></div>' if p is not None else ""
    return (f'<div class="zones">{mark}</div>'
            f'<div class="zlab"><span>0%</span><span>Thấp &lt; {low:.0%}</span><span>Trung bình</span><span>Cao ≥ {high:.0%}</span><span>100%</span></div>')

def stat(label, num, foot, hot=False):
    return f'<div class="stat{" hot" if hot else ""}"><div class="lbl">{label}</div><div class="num">{num}</div><div class="foot">{foot}</div></div>'

def vn(x, nd=1):
    return f"{x:.{nd}f}".replace(".", ",")
