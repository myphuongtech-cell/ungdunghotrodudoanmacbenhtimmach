# CHƯƠNG 5. ỨNG DỤNG, KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

## 5.1. Ứng dụng demo
Ứng dụng viết bằng Streamlit (`app/app.py`) nạp `model_final.joblib`, cho người dùng nhập 13 chỉ số, trả về xác suất nguy cơ (%), mức cảnh báo và biểu đồ các yếu tố làm tăng hoặc giảm nguy cơ của chính người đó. Logic dự đoán và kiểm tra đầu vào nằm trong `src/predict.py`. Mức cảnh báo: dưới 35% là **Thấp**, từ 35% đến dưới 60% là **Trung bình**, từ 60% trở lên là **Cao**. Ngưỡng 35% được chọn bằng dữ liệu (mục 4.7.2) để mô hình phát hiện khoảng 90% ca bệnh; ngưỡng 60% là quy ước của bài. Xác suất chưa được hiệu chỉnh hoàn hảo (hơi cao ở vùng thấp) nên không nên đọc như xác suất mắc bệnh thật. Giao diện luôn hiển thị ghi chú: công cụ không thay thế chẩn đoán của bác sĩ. Cách chạy: `streamlit run app/app.py`.

Dữ liệu nhập được kiểm tra trước khi dự đoán: sai kiểu, thiếu trường hoặc ngoài khoảng hợp lệ (ví dụ tuổi từ 18 đến 100, `thal` từ 1 đến 3) đều trả về thông báo lỗi và không đưa vào mô hình.

## 5.2. Kiểm thử ứng dụng
**Bảng 5.1. Các ca kiểm thử hàm dự đoán**
@@TESTTABLE@@

Cả 9 ca đạt kỳ vọng. Thời gian dự đoán khoảng 8 ms mỗi lần (sau khi mô hình đã nạp), các ca báo lỗi xử lý gần như tức thì. Ca T4 và T5 (mọi biến ở biên) chỉ kiểm tra ứng dụng không bị lỗi, vì tổ hợp này không tương ứng một bệnh nhân thực tế. Ngoài ra có 10 kiểm thử tự động bằng pytest (`tests/test_predict.py`) chạy trong quy trình CI của GitHub (`.github/workflows/ci.yml`). Kiểm thử giao diện tự động (AppTest của Streamlit) xác nhận trang tải được, nút Dự đoán hoạt động và hiển thị xác suất kèm mức cảnh báo. Các ca T1 và T2 lấy từ chính dữ liệu huấn luyện nên chỉ chứng minh ứng dụng chạy đúng, không phải bằng chứng về độ chính xác.

## 5.3. Kết luận
Bài đã hoàn thành chuỗi công việc từ làm sạch dữ liệu (phát hiện và sửa nhãn bị đảo, mã sai, dòng trùng), trực quan hóa, đến xây dựng ba mô hình phân loại và một ứng dụng nhập chỉ số. Các đặc trưng liên quan tới khám gắng sức (loại đau ngực, thalassemia, ST chênh xuống, số mạch hẹp) là nhóm quan trọng nhất, phù hợp với kiến thức y học. Khi đánh giá bằng cross-validation lặp 5x5, năm mô hình hòa nhau (ROC-AUC khoảng 0,90 đến 0,92), nên bài chọn Logistic Regression vì đơn giản và giải thích được. Hạ ngưỡng quyết định xuống 0,35 đưa Recall từ khoảng 0,80 lên khoảng 0,90 (nested CV) với giá phải trả là Precision giảm từ 0,87 xuống 0,73; trên tập test, số ca bỏ sót giảm từ 6 xuống 2 còn số ca báo nhầm tăng từ 4 lên 10.

## 5.4. Hạn chế
1. **Dữ liệu nhỏ** (302 bệnh nhân, tập test 61): kết quả dao động mạnh, chênh lệch giữa các mô hình không đủ chắc để kết luận.
2. **Dữ liệu một nguồn, một nhóm bệnh nhân được chuyển khám:** không đại diện dân số, nên "tỷ lệ có bệnh" là tỷ lệ trong mẫu; mô hình chưa được kiểm chứng trên dữ liệu bên ngoài, đặc biệt chưa kiểm tra với người Việt Nam.
3. **Nhãn trong bản CSV bị đảo và bảng mã một số biến (như `cp`) khác nhau giữa các bản sao;** bài đã sửa nhãn bằng kiểm chứng số liệu nhưng ý nghĩa từng mã `cp` chưa xác minh với tài liệu gốc.
4. **Đánh đổi Recall và Precision:** ở chế độ sàng lọc, khoảng một phần tư số ca báo có bệnh là báo nhầm; việc chọn ngưỡng là quyết định chính sách cần ý kiến chuyên gia y tế. Khoảng tin cậy của kết quả trên tập test còn rộng, và xác suất hơi cao ở vùng thấp.
5. Một số đầu vào (`ca`, `thal`, `oldpeak`) cần xét nghiệm hoặc khám gắng sức chuyên khoa, người dùng thường không tự có.
6. Kết quả có thể lệch nhẹ khi dùng phiên bản thư viện khác (khi chạy lại bằng scikit-learn bản mới hơn, tham số tốt nhất của Random Forest và Accuracy test đổi nhẹ); bài cố định phiên bản trong `requirements.txt`. Các bản scikit-learn khác nhau cũng không đọc được file `.joblib` của nhau một cách đáng tin cậy.
7. Công cụ **không dùng để chẩn đoán**.

## 5.5. Hướng phát triển
Thu thêm dữ liệu hoặc dùng bộ lớn hơn (ví dụ bộ Heart Failure Prediction 918 dòng) để kiểm chứng chéo; hiệu chỉnh xác suất (calibration, ví dụ isotonic) khi có đủ dữ liệu; kiểm tra công bằng theo giới tính và nhóm tuổi trên dữ liệu lớn hơn; so sánh thêm các mô hình dạng bảng hiện đại khi có nhiều dữ liệu; triển khai ứng dụng trực tuyến sau khi có đánh giá của chuyên gia y tế.
