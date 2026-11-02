# Model card: dự đoán nguy cơ bệnh tim mạch

**Mục đích:** bài tập học phần, minh họa quy trình học máy trên dữ liệu y tế. **Không phải thiết bị y tế, không dùng để chẩn đoán hay quyết định điều trị.**

## Mô hình
Logistic Regression (C = 0,1, `class_weight='balanced'`) trong `Pipeline` gồm điền thiếu (median/mode), StandardScaler cho biến số, One-Hot cho `cp, restecg, slope, thal`. Huấn luyện lại trên toàn bộ 302 bệnh nhân (`models/model_final.joblib`). Phiên bản thư viện: xem `requirements.txt` (scikit-learn 1.8.0).

## Dữ liệu
Heart Disease, phần Cleveland (UCI), 303 dòng, sau làm sạch 302. Nhãn gốc `target` bị đảo, bài dùng `HeartDisease = 1 − target`. Chi tiết: `notebooks/01_eda.ipynb`, `02_cleaning.ipynb`.

## Hiệu năng (không phải đo trên chính dữ liệu huấn luyện)
| Phép đánh giá | Kết quả |
|---|---|
| CV lặp 5x5, ngưỡng 0,5 | Recall 0,804 ± 0,090; Precision 0,873; ROC-AUC 0,917; Brier 0,117 |
| Nested CV, ngưỡng sàng lọc (~0,35) | Recall 0,897 ± 0,077; Precision 0,727 |
| Test giữ riêng 61 mẫu, ngưỡng 0,35 | Recall 0,929 (KTC 95%: 0,83 đến 1,00); Precision 0,722; bỏ sót 2, báo nhầm 10 |

## Ngưỡng và mức cảnh báo
Thấp: dưới 0,35 (ngưỡng chọn để Recall từ 0,90); Cao: từ 0,60 (quy ước); Trung bình: ở giữa. Chọn ngưỡng là đánh đổi giữa bỏ sót ca bệnh và báo nhầm, cần ý kiến chuyên gia y tế.

## Giới hạn đã biết
- Dữ liệu nhỏ, một nguồn, nhóm bệnh nhân được chuyển khám tại một cơ sở ở Mỹ, thu thập thập niên 1980; chưa kiểm chứng trên người Việt Nam hay dân số chung.
- Xác suất hơi cao ở vùng thấp (xem `notebooks/04_optimization.ipynb`, mục hiệu chuẩn).
- Nhóm nữ chỉ có 4 ca bệnh trong tập test nên chưa đánh giá được công bằng theo giới.
- Một số đầu vào (`ca`, `thal`, `oldpeak`) cần khám chuyên khoa.
- Bảng mã của các biến phân loại (như `cp`) chưa được đối chiếu với tài liệu gốc.
