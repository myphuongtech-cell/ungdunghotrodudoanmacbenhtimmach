# Đề tài 2: Dự đoán nguy cơ bệnh tim mạch (Python, HK1 2026-2027)

Tiến độ: đã xong dữ liệu, trực quan hóa, mô hình, tối ưu hóa nâng cao, ứng dụng Streamlit có giải thích từng ca, kiểm thử tự động và báo cáo Word (Chương 1-5).

## Cài đặt và chạy
```
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd notebooks && jupyter nbconvert --to notebook --execute --inplace 01_eda.ipynb 02_cleaning.ipynb 02b_visualization.ipynb 03_modeling.ipynb 04_optimization.ipynb
```
Chạy theo thứ tự 01, 02, 02b, 03, 04 (02 tạo `data/heart_clean.csv`, 03 tạo `models/model.joblib` là Random Forest giai đoạn đầu, 04 tạo `models/model_final.joblib` là mô hình triển khai).

Chạy ứng dụng: `streamlit run app/app.py` (giao diện dashboard 3 tab: Tổng quan, Dự đoán, Mô hình; CSS trong `app/style.py`, cấu hình giao diện trong `.streamlit/config.toml`). Cần chạy từ thư mục gốc của dự án. Kiểm thử: `pytest` (10 kiểm thử, cũng chạy trong CI GitHub) và `python src/test_app.py` (ghi `report/bang_kiem_thu.csv`).

Lưu ý: số liệu trong báo cáo sinh ra với scikit-learn 1.8.0 (đã ghim trong `requirements.txt`); bản mới hơn cho kết quả lệch nhẹ.

## Cấu trúc
- `data/` dữ liệu gốc, dữ liệu sạch, bảng mô tả cột
- `notebooks/` 01_eda, 02_cleaning, 02b_visualization, 03_modeling, 04_optimization (CV lặp, chọn ngưỡng nested, hiệu chuẩn, khoảng tin cậy, giải thích)
- `MODEL_CARD.md` mô tả mô hình, hiệu năng và giới hạn; `tests/` và `.github/workflows/ci.yml` kiểm thử tự động
- `src/common.py` tiền xử lý dùng chung (Pipeline); `src/build_notebooks.py` sinh notebook
- `figures/` hình cho báo cáo; `models/` mô hình đã lưu; `report/` bảng kết quả và bản nháp chương
- `app/app.py` ứng dụng Streamlit; `src/predict.py` hàm dự đoán và kiểm tra đầu vào; `src/test_app.py` kiểm thử
- `report/BaoCao_DeTai2.docx` báo cáo (Chương 1-5); `report/final/` nguồn markdown của báo cáo; `src/build_report.js` dựng file Word

## Nguồn dữ liệu
Heart Disease, phần Cleveland (UCI Machine Learning Repository), bản CSV từ GitHub `kb22/Heart-Disease-Prediction`. Cần kiểm tra giấy phép trước khi nộp. Nhãn gốc `target` bị đảo, bài dùng `HeartDisease = 1 - target` (xem notebook 01).

Công cụ học tập, không thay thế chẩn đoán của bác sĩ.
