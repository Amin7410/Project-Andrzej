# Tình trạng Dự án & Phân tích Kỹ thuật

Tài liệu này cung cấp cái nhìn rõ ràng về những gì `eml_sr` có thể làm được hiện nay, những lợi ích cốt lõi và các hạn chế quan trọng mà bạn cần lưu ý để đảm bảo trải nghiệm mượt mà.

## Tình trạng hiện tại (v0.1.0)

`eml_sr` hiện đang ở giai đoạn phát hành sớm ổn định. Thư viện đã sẵn sàng cho các nhiệm vụ sau:
- **Hồi quy Đơn biến & Đa biến**: Tìm kiếm công thức cho các hàm có một hoặc nhiều biến số.
- **Khám phá Pareto-Front**: Trả về danh sách các công thức ứng viên được tối ưu hóa cân bằng giữa độ chính xác và độ phức tạp.
- **Tinh chỉnh Hằng số**: Tích hợp bộ tối ưu hóa Levenberg-Marquardt để xác định hằng số với độ chính xác cao.
- **Hỗ trợ Đa nền tảng**: Hỗ trợ chính thức cho Windows (x64), Linux (x86_64), và macOS (Intel/Apple Silicon).

## Tham chiếu Cấu hình Mặc định

Hiểu rõ các giá trị mặc định sẽ giúp bạn quyết định cách tinh chỉnh động cơ cho phù hợp với phần cứng của mình:

max_complexity : 6 - Độ sâu tối đa của cây biểu thức. 
beam_width : 1000 - Số ứng viên giữ lại mỗi cấp độ (Quan trọng cho RAM). 
precision_goal : 1e-10 - Ngưỡng sai số để dừng tìm kiếm sớm. 
complexity_penalty : 0.1 - Hình phạt để ưu tiên các công thức đơn giản. 
optimize_constants : true - Bật tính năng tinh chỉnh hằng số độ chính xác cao. 

## Lợi ích Cốt lõi

1. **Tốc độ Cực lớn**: Được xây dựng trên động cơ Rust đa luồng, thư viện có thể xử lý hàng triệu biểu thức mỗi giây.
2. **AI có khả năng giải thích**: Xuất ra các công thức toán học sắc nét, dễ hiểu thay vì các trọng số "hộp đen".
3. **Tính đồng nhất về Kiến trúc**: Sử dụng toán tử EML đảm bảo mọi kết quả đều có cấu trúc đồng nhất, lý tưởng cho việc biên dịch phần cứng hoặc xác minh hình thức.

## ⚠️ Hạn chế Quan trọng & Cảnh báo An toàn

### 1. Quản lý Bộ nhớ (Cảnh báo về `beam_width`)
Nguyên nhân phổ biến nhất gây ra treo hệ thống hoặc lỗi "Tràn bộ nhớ" (Out of Memory - OOM) là do cấu hình **Beam Width** không phù hợp.
- **Cơ chế hoạt động**: Ở mỗi cấp độ phức tạp, bộ tìm kiếm sẽ giữ lại `N` ứng viên tốt nhất (với `N` là `beam_width`).
- **Rủi ro**: Nếu bạn đặt `beam_width` quá cao (ví dụ: 5.000, 10.000 hoặc hơn) trên một máy tính có RAM hạn chế (8GB hoặc 16GB), lượng bộ nhớ sử dụng sẽ bùng nổ theo cấp số nhân khi quá trình tìm kiếm tiến sâu hơn.
- **Khuyến nghị**: Hãy bắt đầu với `beam_width` khoảng **500 - 1.000**. Chỉ tăng giá trị này nếu máy tính của bạn có lượng RAM dư dả và bài toán yêu cầu tìm kiếm rất sâu.

### 2. Sự bùng nổ không gian tìm kiếm
Việc tăng `max_complexity` sẽ thêm các nút vào cây EML. Số lượng cấu trúc cây có thể có tăng theo cấp số nhân.
- **Mẹo**: Hầu hết các định luật vật lý có thể được tìm thấy trong phạm vi độ phức tạp từ **10 - 15**. Tránh đặt cao hơn trừ khi thực sự cần thiết, vì nó sẽ làm tăng đáng kể thời gian tìm kiếm.

### 3. Độ ổn định số học
Vì các cây EML có thể trở nên rất sâu (lồng ghép các hàm mũ và logarit), độ chính xác của số phẩy động trở thành một yếu tố quan trọng.
- **Hiện tượng**: Các cây cực sâu có thể gặp lỗi "catastrophic cancellation" hoặc tràn/dưới mức (overflow/underflow).
- **Cách xử lý**: Sử dụng `allow_approximate: true` trong cấu hình để cho phép bộ tìm kiếm bỏ qua các nhánh không ổn định về mặt số học.

### 4. Sự hội tụ trong tối ưu hóa hằng số
Mặc dù chúng tôi sử dụng thuật toán Levenberg-Marquardt, đây là một bộ tối ưu hóa cục bộ.
- **Cảnh báo**: Nếu cấu trúc ban đầu tìm được quá xa so với thực tế, việc tối ưu hóa hằng số có thể bị kẹt ở cực tiểu cục bộ. Bộ tìm kiếm phụ thuộc vào việc tìm ra một cấu trúc "đủ tốt" trước khi tinh chỉnh hằng số.

---
*Bằng cách hiểu rõ các giới hạn này, bạn có thể khai thác toàn bộ sức mạnh của EML-SR mà không làm treo môi trường làm việc của mình.*
