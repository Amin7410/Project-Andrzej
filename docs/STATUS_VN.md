# Tình trạng Dự án & Phân tích Kỹ thuật

Tài liệu này cung cấp cái nhìn rõ ràng về những gì `eml_sr` có thể làm được hiện nay, những lợi ích cốt lõi và các hạn chế quan trọng mà bạn cần lưu ý để đảm bảo trải nghiệm mượt mà.

## Tình trạng hiện tại (v0.2.2)

`eml_sr` hiện đang ở giai đoạn sản xuất được tối ưu hóa cao và ổn định. Các cập nhật gần đây (v0.2.1 và v0.2.2) mang tới nhiều cải tiến đột phá:
- **Lớp bọc tìm kiếm thông minh Python (`SmartSearcher`)**: Tích hợp tầng biến đổi dữ liệu đầu ra ở mức Python để tự động tìm kiếm trên các mục tiêu đã được chuyển đổi ($y$, $y^2$, $\ln(y)$, $1/y$) nhằm giải quyết các mối quan hệ phi tuyến (như căn thức hoặc nghịch đảo phân số).
- **Biên Pareto hợp nhất và Ánh xạ ngược**: Tự động chuyển đổi các công thức ứng viên về hệ tọa độ gốc, tính toán lại sai số MSE thực tế, tự động cộng thêm chi phí cấu trúc (+1 nút cho hàm bọc nghịch đảo) để đảm bảo biên Pareto chuẩn xác.
- **Chiến lược Ngắt Sớm (Early Stop)**: Ngắt toàn bộ vòng lặp tìm kiếm giữa các chiến lược ngay khi phát hiện công thức đúng hoàn hảo (MSE thực tế $< 10^{-15}$), tiết kiệm tới 75% thời gian chạy máy.
- **Lọc đa dạng cấu trúc Quality-Diversity (QD)**: Thay đổi bộ lọc chùm tia (beam selection) trong BFS Rust sang tỷ lệ 80% dựa trên sai số (Quality) và 20% ưu tiên các cấu trúc độc đáo (Diversity) để tránh hiện tượng đơn điệu hóa chùm tia.
- **Bảo vệ tối ưu hóa Levenberg-Marquardt**: Tự động ngắt tối ưu LM sớm nếu sau 3 vòng lặp liên tiếp không cải thiện sai số hoặc nếu hệ số cản $\lambda > 10^4$ để tiết kiệm CPU.
- **Thêm các toán tử lũy thừa tích hợp**: Bổ sung sẵn `Square` ($x^2$) và `Cube` ($x^3$) vào tập toán tử nhằm tối ưu hóa độ sâu cây biểu thức.
- **Kiến trúc tham số động Model-First**: Hằng số được biểu diễn dưới dạng các nút tham số động (`Node::Param`) thay vì các số đóng băng tĩnh.
- **Bộ tối ưu hóa Levenberg-Marquardt sửa đổi**: Thay thế các bước SGD bằng thuật toán Marquardt Diagonal Scaling để đảm bảo sự hội tụ mạnh mẽ.
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
Sử dụng tệp sinh ở thư mục gốc để tự động tạo cấu trúc thư mục kiểm thử phân cấp:
```bash
python generate_suite.py
```
Lệnh này sẽ tự động đọc tập dữ liệu, dọn dẹp các kịch bản cũ và tạo ra cấu trúc thư mục `Test/Feynman/` chứa toàn bộ 100 phương trình kiểm thử.

### 3. Chạy từng phương trình Feynman cụ thể (Ví dụ: Hiệu ứng Doppler `I_34_1`)
Mỗi bài toán được quy hoạch trong thư mục riêng biệt `Test/Feynman/<ID>/` và sử dụng cấu hình tìm kiếm thích ứng:
```bash
# Chạy một bài test cụ thể bằng môi trường ảo Python
.venv/Scripts/python -u Test/Feynman/I_34_1/test.py
```
Kết quả (file log Pareto-Front `fit.txt` và đồ thị hồi quy `fit.png`) sẽ được tự động lưu tại thư mục `Test/Feynman/<ID>/Results/`.

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
