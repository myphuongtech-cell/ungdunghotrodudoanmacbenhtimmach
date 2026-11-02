# CHƯƠNG 4. MÔ HÌNH VÀ ĐÁNH GIÁ (ghi chú kết quả, chưa phải bản nháp hoàn chỉnh)

Nguồn: `notebooks/03_modeling.ipynb`; bảng trong `report/*.csv`. Hạn viết Chương 4 trong Notion là 1/11, đây là số liệu để bạn viết tiếp.

**Thiết lập.** Chia 80/20 có stratify, random_state = 42: train 241, test 61 (28 ca có bệnh). Bộ tiền xử lý nằm trong Pipeline. Ba mô hình: Logistic Regression, Random Forest, Gradient Boosting.

**Kết quả trên tập test sau tinh chỉnh (GridSearchCV, chọn theo F2):**
| Mô hình | Accuracy | Precision | Recall | F1 | ROC-AUC | CV Recall | CV ROC-AUC |
|---|---|---|---|---|---|---|---|
| Logistic Regression | 0,836 | 0,846 | 0,786 | 0,815 | 0,924 | 0,827 | 0,908 |
| Random Forest | 0,803 | 0,833 | 0,714 | 0,769 | 0,884 | 0,845 | 0,916 |
| Gradient Boosting | 0,820 | 0,870 | 0,714 | 0,784 | 0,893 | 0,809 | 0,895 |

**Mô hình được chọn theo quy tắc đặt trước (CV F2 cao nhất): Random Forest** (max_depth 3, min_samples_leaf 3, 200 cây; CV F2 0,837 so với 0,825 của Logistic Regression). Confusion Matrix của mô hình này trên test: 29 đúng không bệnh, 4 báo nhầm, 8 bỏ sót, 20 đúng có bệnh.

**Điều cần nói thẳng trong báo cáo và khi vấn đáp**
1. Với mục tiêu ưu tiên Recall, mô hình được chọn bỏ sót 8/28 ca (Recall test 0,714). Logistic Regression có Recall test 0,786 và ROC-AUC test 0,924, cao hơn trên test dù thấp hơn nhẹ trên CV.
2. Chênh lệch giữa các mô hình nhỏ so với độ nhiễu: tập test chỉ có 61 mẫu (mỗi ca bệnh bị bỏ sót làm Recall đổi khoảng 3,6 điểm phần trăm) và độ lệch chuẩn Recall giữa các fold CV là 0,06 đến 0,08. Không nên khẳng định mô hình nào "tốt hơn" một cách chắc chắn.
3. Random Forest và Gradient Boosting mặc định đạt Accuracy train 1,0 so với test 0,79 đến 0,80: dấu hiệu overfitting. Logistic Regression ổn định hơn (train 0,876, test 0,836). Việc tinh chỉnh giảm độ sâu cây là để giảm overfitting.
4. Hướng cải thiện Recall mà vẫn đúng quy trình: hạ ngưỡng quyết định (dưới 0,5) với ngưỡng chọn bằng cross-validation trên train, rồi báo cáo đánh đổi với Precision. Chưa làm trong lần này.

**Feature Importance** (`fig_4_3`, `fig_4_4`). Permutation importance (giảm F2 trên test): `cp` (0,072), `thal` (0,037), `oldpeak` (0,028), `ca` (0,020), các biến còn lại gần 0. Độ quan trọng nội tại của Random Forest: `thal_2`, `thal_3`, `ca`, `exang`, `cp_0`, `oldpeak` đứng đầu. Các biến này hợp lý về y học (loại đau ngực, khuyết tật tưới máu cơ tim, ST chênh xuống khi gắng sức, số mạch hẹp). Hai điểm lưu ý: permutation importance của `exang` và `thalach` xấp xỉ 0 không có nghĩa chúng vô dụng, vì chúng tương quan với `cp` và `oldpeak` nên thông tin bị chia sẻ; `sex` có giá trị âm nhẹ (−0,023), tức xáo trộn nó lại làm F2 tốt lên, một dấu hiệu nhiễu trên tập test nhỏ.

**Đã lưu:** `models/model.joblib` (pipeline đầy đủ) và `models/model_meta.json`; nạp lại cho xác suất dự đoán giống hệt trên tập test.
