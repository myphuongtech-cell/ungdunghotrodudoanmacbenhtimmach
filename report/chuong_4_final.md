# CHƯƠNG 4. MÔ HÌNH VÀ ĐÁNH GIÁ

Mã nguồn: `notebooks/03_modeling.ipynb`.

## 4.1. Thiết lập thực nghiệm
Dữ liệu sạch (302 bệnh nhân) được chia 80/20 có phân tầng theo nhãn (`stratify`) với `random_state = 42`: tập train 241 mẫu, tập test 61 mẫu (28 ca có bệnh). Mọi bước tiền xử lý (điền thiếu, chuẩn hóa, One-Hot) nằm trong `Pipeline` và chỉ fit trên tập train, do đó thông tin của tập test không rò rỉ vào mô hình. Ba mô hình được so sánh: Logistic Regression (baseline), Random Forest và Gradient Boosting.

Vì bỏ sót ca bệnh nguy hiểm hơn báo nhầm ca khỏe, tiêu chí ưu tiên là **Recall của nhóm có bệnh**. Khi tinh chỉnh, bài dùng điểm **F2** (trọng số Recall gấp đôi Precision) để chọn tham số.

## 4.2. Kết quả trước khi tinh chỉnh
**Bảng 4.1. Kết quả trên tập test và cross-validation 5 fold (trước tinh chỉnh)**
| Mô hình | Accuracy | Precision | Recall | F1 | ROC-AUC | CV Recall | CV ROC-AUC |
|---|---|---|---|---|---|---|---|
| Logistic Regression | 0,836 | 0,821 | 0,821 | 0,821 | 0,926 | 0,818 | 0,903 |
| Random Forest | 0,787 | 0,800 | 0,714 | 0,755 | 0,889 | 0,809 | 0,904 |
| Gradient Boosting | 0,803 | 0,786 | 0,786 | 0,786 | 0,887 | 0,782 | 0,873 |

Random Forest và Gradient Boosting mặc định đạt Accuracy 1,0 trên train nhưng chỉ 0,79 đến 0,80 trên test, một dấu hiệu overfitting rõ. Logistic Regression ổn định hơn (train 0,876, test 0,836).

![Hình 4.1. Confusion Matrix trên tập test (ba mô hình trước tinh chỉnh)](fig_4_1_confusion_matrix.png)

![Hình 4.2. Đường ROC trên tập test (ba mô hình trước tinh chỉnh)](fig_4_2_roc.png)

## 4.3. Tinh chỉnh siêu tham số
GridSearchCV 5 fold, chọn theo F2, lưới tham số nhỏ do dữ liệu ít.
**Bảng 4.2. Tham số tốt nhất và điểm cross-validation**
| Mô hình | Tham số tốt nhất | CV F2 | CV Recall | CV ROC-AUC |
|---|---|---|---|---|
| Logistic Regression | C = 0,1; penalty = l2 | 0,825 | 0,827 | 0,908 |
| Random Forest | max_depth = 3; min_samples_leaf = 3; n_estimators = 200 | 0,837 | 0,845 | 0,916 |
| Gradient Boosting | learning_rate = 0,03; max_depth = 2; n_estimators = 100 | 0,804 | 0,809 | 0,895 |

**Bảng 4.3. Kết quả trên tập test sau tinh chỉnh**
| Mô hình | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| Logistic Regression | 0,836 | 0,846 | 0,786 | 0,815 | 0,924 |
| Random Forest | 0,803 | 0,833 | 0,714 | 0,769 | 0,884 |
| Gradient Boosting | 0,820 | 0,870 | 0,714 | 0,784 | 0,893 |

## 4.4. Lựa chọn mô hình và thảo luận
Theo tiêu chí đặt trước (CV F2 cao nhất, không dựa vào tập test) mô hình được chọn là **Random Forest** (CV F2 = 0,837 so với 0,825 của Logistic Regression). Trên tập test, mô hình đã tinh chỉnh này (Hình 4.1 vẽ các mô hình trước tinh chỉnh nên số liệu khác) đúng 29 ca không bệnh, báo nhầm 4, bỏ sót 8 và phát hiện đúng 20 ca có bệnh.

Cần đọc kết quả thận trọng vì ba lý do. Thứ nhất, Recall test của mô hình chọn là 0,714 (bỏ sót 8/28 ca), thấp hơn Logistic Regression (0,786) dù mục tiêu là ưu tiên Recall. Thứ hai, chênh lệch giữa các mô hình nhỏ so với nhiễu: tập test chỉ 61 mẫu nên mỗi ca bỏ sót làm Recall đổi khoảng 3,6 điểm phần trăm, và độ lệch chuẩn của Recall giữa các fold là 0,06 đến 0,08. Vì vậy báo cáo không khẳng định mô hình nào vượt trội. Thứ ba, kết quả là điểm ước lượng trên dữ liệu nhỏ, chưa kiểm chứng trên dữ liệu bên ngoài. Một hướng cải thiện Recall là hạ ngưỡng quyết định dưới 0,5 (chọn ngưỡng bằng cross-validation trên train) và chấp nhận Precision giảm, chưa thực hiện trong bài này.

## 4.5. Feature Importance
Permutation importance (mức giảm F2 khi xáo trộn một đặc trưng, trên tập test, 30 lần lặp) xếp `cp` (0,072), `thal` (0,037), `oldpeak` (0,028) và `ca` (0,020) đứng đầu, các biến còn lại gần 0.

![Hình 4.3. Permutation importance của mô hình Random Forest](fig_4_3_feature_importance.png)

Độ quan trọng nội tại của Random Forest (Hình 4.4) cho bức tranh tương tự, với `thal`, `ca`, `exang`, `cp` và `oldpeak` ở nhóm đầu.

![Hình 4.4. Độ quan trọng nội tại của Random Forest (10 đặc trưng đầu)](fig_4_4_rf_importance.png)

Các đặc trưng này hợp lý về y học: loại đau ngực, kết quả thalassemia (liên quan khuyết tật tưới máu cơ tim), ST chênh xuống khi gắng sức và số mạch hẹp đều là dấu hiệu thiếu máu cơ tim. Kết quả cũng khớp với Chương 3, nơi các biến này có tương quan mạnh nhất với nhãn. Hai lưu ý: `exang` và `thalach` có permutation importance xấp xỉ 0 không có nghĩa là vô dụng, vì chúng tương quan với `cp` và `oldpeak` nên thông tin bị chia sẻ; và `sex` có giá trị âm nhẹ (−0,023), tức xáo trộn nó lại làm F2 tốt lên, một dấu hiệu nhiễu trên tập test nhỏ.

## 4.6. Lưu mô hình
Pipeline hoàn chỉnh được lưu bằng `joblib` (`models/model.joblib`, khoảng 328 KB) cùng file mô tả `model_meta.json`. Đoạn mã nạp lại và so sánh xác suất dự đoán trên tập test cho kết quả trùng khớp hoàn toàn.
