# CHƯƠNG 1. TỔNG QUAN ĐỀ TÀI (bản nháp)

> Bản nháp để bạn viết lại bằng lời của mình. Những chỗ trong ngoặc vuông [ ] cần bạn điền hoặc kiểm tra trước khi nộp.

## 1.1. Bối cảnh
Bệnh tim mạch là nhóm bệnh của tim và mạch máu, được WHO xếp vào nguyên nhân tử vong hàng đầu trên toàn cầu [điền số liệu mới nhất từ trang WHO "Cardiovascular diseases (CVDs)" và ghi ngày truy cập]. Nhiều ca có thể phòng ngừa nếu phát hiện sớm các yếu tố nguy cơ như tuổi, huyết áp, cholesterol, đau ngực khi gắng sức hay bất thường trên điện tâm đồ. Các chỉ số này được ghi nhận thường quy trong khám tim mạch, nên có thể dùng làm đầu vào cho mô hình học máy hỗ trợ sàng lọc.

## 1.2. Mục tiêu
1. Làm sạch và phân tích dữ liệu y tế về bệnh tim bằng Python (pandas, Matplotlib, Seaborn).
2. Xây dựng và so sánh ít nhất hai (trong bài này là ba) mô hình phân loại: Logistic Regression, Random Forest, Gradient Boosting; đánh giá bằng Accuracy, Precision, Recall, F1, Confusion Matrix, ROC-AUC và xác định các đặc trưng quan trọng.
3. Xây dựng ứng dụng nhập chỉ số cá nhân và trả về cảnh báo nguy cơ [mục tiêu này hoàn thành ở giai đoạn sau, xem Chương 5].

Do bỏ sót một ca bệnh nguy hiểm hơn báo nhầm một ca khỏe, bài ưu tiên **Recall của nhóm có bệnh**, đồng thời theo dõi Precision và F1 để không báo động quá mức.

## 1.3. Dữ liệu
Bộ dữ liệu Heart Disease, phần Cleveland của UCI Machine Learning Repository: 303 bệnh nhân, 13 đặc trưng lâm sàng và 1 nhãn (Bảng 1.1, xem `data/data_dictionary.csv`). Nhiều bản sao của bộ dữ liệu này lưu hành trên mạng; bản dùng trong bài lấy từ kho GitHub `kb22/Heart-Disease-Prediction` [kiểm tra giấy phép của bản này và của UCI rồi ghi vào đây]. Chi tiết xử lý ở Chương 2.

## 1.4. Phạm vi và giới hạn
Đây là bài tập học phần trên bộ dữ liệu nhỏ của một nhóm bệnh nhân được chuyển tới khám, không phải mẫu đại diện dân số. Mô hình chỉ có tính tham khảo giáo dục, **không thay thế chẩn đoán của bác sĩ**.

## 1.5. Bố cục báo cáo
Chương 1: Tổng quan. Chương 2: Dữ liệu và xử lý. Chương 3: Trực quan hóa và insight. Chương 4: Mô hình và đánh giá. Chương 5: Ứng dụng, kết luận, hạn chế và hướng phát triển.
