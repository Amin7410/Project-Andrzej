# Tình trạng Dự án & Phân tích Kỹ thuật

Tài liệu này cung cấp cái nhìn rõ ràng về những gì `eml_sr` có thể làm được hiện nay, những lợi ích cốt lõi và các hạn chế quan trọng mà bạn cần lưu ý để đảm bảo trải nghiệm mượt mà.

## Tình trạng hiện tại (v0.2.0)

`eml_sr` hiện đang ở giai đoạn sản xuất được tối ưu hóa cao và ổn định. Trong phiên bản `v0.2.0`, các cải tiến lớn về cấu trúc toán học và kiến trúc hệ thống đã được giới thiệu:
- **Kiến trúc tham số động Model-First**: Hằng số được biểu diễn dưới dạng các nút tham số động (`Node::Param`) thay vì các số đóng băng tĩnh, cho phép tối ưu hóa đồng thời các hằng số lồng nhau qua các cấp độ phức tạp mà không làm lãng phí độ sâu (độ phức tạp) của cây biểu thức.
- **Bộ tối ưu hóa Levenberg-Marquardt sửa đổi**: Thay thế các bước SGD đơn giản bằng thuật toán Marquardt Diagonal Scaling để đảm bảo sự hội tụ mạnh mẽ, ổn định của các tham số phi tuyến ngay cả khi nằm sâu trong các hàm lồng nhau.
- **Tối ưu hóa Elastic Net ($L_1 + L_2$)**: Tích hợp các ràng buộc phạt độ lớn tham số trực tiếp vào hàm sai số tìm kiếm để thúc đẩy tính thưa hóa (sparsity) và ngăn ngừa mất ổn định số học.
- **Tối ưu hóa hằng số hai giai đoạn (Dual-Phase)**: Sử dụng tối ưu hóa LM 10 vòng lặp nhanh trong quá trình duyệt BFS để tiết kiệm CPU và chạy tối ưu hóa LM 30 vòng lặp sâu trên các ứng viên Pareto-Front cuối cùng để đạt độ chính xác tối đa.
- **Log tiến trình & ETA song song**: Bộ đếm song song lock-free hiển thị tiến trình tìm kiếm tại mỗi mốc 10%, kèm theo thời gian trôi qua và thời gian còn lại dự kiến (ETA).
- **Hồi quy Đơn biến & Đa biến**: Tìm kiếm công thức cho các hàm có một hoặc nhiều biến số.
- **Khám phá Pareto-Front**: Trả về danh sách các công thức ứng viên được tối ưu hóa cân bằng giữa độ chính xác và độ phức tạp.
- **Hỗ trợ Đa nền tảng**: Hỗ trợ chính thức cho Windows (x64), Linux (x86_64), và macOS (Intel/Apple Silicon).

## Tham chiếu Cấu hình Mặc định

Hiểu rõ các giá trị mặc định sẽ giúp bạn quyết định cách tinh chỉnh động cơ cho phù hợp với phần cứng của mình:
- `max_complexity` : 6 - Độ sâu tối đa của cây biểu thức.
- `beam_width` : 200 - Số ứng viên giữ lại mỗi cấp độ (Quan trọng cho RAM; mặc định được hạ từ 1000 xuống 200 để mở rộng đa lõi an toàn).
- `precision_goal` : 1e-10 - Ngưỡng sai số để dừng tìm kiếm sớm.
- `complexity_penalty` : 0.1 - Hình phạt để ưu tiên các công thức đơn giản hơn.
- `optimize_constants` : true - Bật tính năng tinh chỉnh hằng số độ chính xác cao.
- `alpha` : 0.0 - Hệ số nhân phạt Elastic Net (độ mạnh của phạt L1 + L2).
- `l1_ratio` : 0.5 - Tỷ lệ giữa phạt L1 (Lasso) và phạt L2 (Ridge).

## Lợi ích Cốt lõi

1. **Tốc độ Cực lớn**: Được xây dựng trên động cơ Rust đa luồng (song song hóa qua Rayon), thư viện có thể xử lý hàng triệu biểu thức mỗi giây.
2. **AI có khả năng giải thích**: Xuất ra các công thức toán học sắc nét, dễ đọc (với các hằng số tối ưu thực tế được định dạng sẵn) thay vì các trọng số "hộp đen".
3. **Tính đồng nhất về Kiến trúc**: Sử dụng toán tử EML đảm bảo mọi kết quả đều có cấu trúc đồng nhất, lý tưởng cho việc biên dịch phần cứng hoặc xác minh hình thức.

---

## 🛠 Hướng dẫn Chạy Kiểm thử & Nhà phát triển

### 1. Biên dịch lại Python Bindings
Nếu bạn chỉnh sửa mã nguồn Rust, hãy biên dịch lại tiện ích mở rộng Python bằng Maturin. Trên Windows PowerShell:
```powershell
$env:PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1; .venv\Scripts\maturin.exe develop
```

### 2. Sinh bộ kiểm thử Feynman Equations
Sử dụng tệp sinh ở thư mục gốc để tự động tạo thư mục kiểm thử:
```bash
python generate_suite.py
```
Lệnh này sẽ đọc dữ liệu, xóa các tệp cũ và tạo ra một thư mục `Test/` (được git bỏ qua) chứa bộ test dễ và 92 bài test khó riêng biệt.

### 3. Chạy bộ kiểm thử dễ (7 phương trình)
Xác minh khả năng tìm kiếm cơ bản dưới cấu hình tiêu chuẩn (`max_complexity=6`, `beam_width=200`):
```bash
python Test/test_easy.py
```

### 4. Chạy từng phương trình khó cụ thể (Ví dụ: Khối lượng tương đối tính Einstein `I.10.7`)
Chạy bài test độ khó cao với cấu hình `max_complexity=8` và `beam_width=500`:
```bash
python Test/test_diff_I_10_7.py
```

---

## ⚠️ Hạn chế Quan trọng & Cảnh báo An toàn

### 1. Quản lý Bộ nhớ (Cảnh báo về `beam_width`)
Nguyên nhân phổ biến nhất gây ra treo hệ thống hoặc lỗi "Tràn bộ nhớ" (Out of Memory - OOM) là do cấu hình **Beam Width** không phù hợp.
- **Cơ chế hoạt động**: Ở mỗi cấp độ phức tạp, bộ tìm kiếm sẽ giữ lại `N` ứng viên tốt nhất (với `N` là `beam_width`).
- **Rủi ro**: Nếu bạn đặt `beam_width` quá cao (ví dụ: 5.000, 10.000 hoặc hơn) trên một máy tính có RAM hạn chế, lượng bộ nhớ sử dụng sẽ bùng nổ theo cấp số nhân khi quá trình tìm kiếm tiến sâu hơn.
- **Khuyến nghị**: Hãy bắt đầu với `beam_width` khoảng **200 - 500**. Chỉ tăng giá trị này nếu máy tính của bạn có lượng RAM dư dả và bài toán yêu cầu tìm kiếm rất sâu.

### 2. Sự bùng nổ không gian tìm kiếm
Việc tăng `max_complexity` sẽ thêm các nút vào cây EML. Số lượng cấu trúc cây có thể có tăng theo cấp số nhân.
- **Mẹo**: Hầu hết các định luật vật lý có thể được tìm thấy trong phạm vi độ phức tạp từ **8 - 12**. Tránh đặt cao hơn trừ khi thực sự cần thiết, vì nó sẽ làm tăng đáng kể thời gian tìm kiếm.

### 3. Độ ổn định số học
Vì các cây EML có thể trở nên rất sâu (lồng ghép các hàm mũ và logarit), độ chính xác của số phẩy động trở thành một yếu tố quan trọng.
- **Hiện tượng**: Các cây cực sâu có thể gặp lỗi "catastrophic cancellation" hoặc tràn/dưới mức (overflow/underflow).
- **Cách xử lý**: Sử dụng `allow_approximate: true` trong cấu hình để cho phép bộ tìm kiếm bỏ qua các nhánh không ổn định về mặt số học.

### 4. Sự hội tụ trong tối ưu hóa hằng số
Mặc dù chúng tôi sử dụng thuật toán Levenberg-Marquardt, đây là một bộ tối ưu hóa cục bộ.
- **Cảnh báo**: Nếu cấu trúc ban đầu tìm được quá xa so với thực tế, việc tối ưu hóa hằng số có thể bị kẹt ở cực tiểu cục bộ. Bộ tìm kiếm phụ thuộc vào việc tìm ra một cấu trúc "đủ tốt" trước khi tinh chỉnh hằng số.
