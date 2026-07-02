# Hướng dẫn đóng góp cho eml_sr

Tài liệu này dành cho các nhà phát triển muốn biên dịch `eml_sr` từ mã nguồn, chạy các kịch bản demo/ví dụ, hoặc đóng góp vào dự án.

Lưu ý: dự án hiện **chưa có bộ test tự động** (không có hàm `#[test]`, CI không chạy `cargo test`). Các bước "kiểm nghiệm" bên dưới là kiểm tra thủ công, không phải test hồi quy tự động. Rất hoan nghênh đóng góp thêm test `#[test]` thật — xem [STATUS_VN.md](STATUS_VN.md) để biết đầy đủ các khoảng trống đã biết.

## Thiết lập Phát triển

### 1. Chạy các kịch bản kiểm nghiệm demo
Sau khi tải mã nguồn về, bạn có thể chạy một số kịch bản demo viết tay (xem `src/tests/mod.rs`) để thấy engine hoạt động:
```bash
cargo run --release
```
Lệnh này in ra công thức tìm được và kết quả kiểu pass/fail cho một số kịch bản — đây không phải bộ test tự động.

### 2. Xem các ví dụ mẫu sinh động
Chúng tôi cung cấp thư mục `examples/` để bạn học cách sử dụng qua thực tế. Hãy thử chạy các lệnh sau:
```bash
# Tìm hàm đơn biến
cargo run --release --example 01_simple_discovery

# Tìm hàm đa biến
cargo run --release --example 02_multivariate

# Nhận diện hằng số toán học
cargo run --release --example 03_constant_recognition
```

### 3. Tự thêm kịch bản demo của riêng bạn
Bạn có thể thử bất kỳ hàm số nào bằng cách mở file `src/tests/mod.rs` và thêm một `TestCase` mới vào hàm `get_test_suite()`. Nó sẽ xuất hiện trong báo cáo khi bạn chạy `cargo run`. Đây là cơ chế demo thủ công, không phải test tự động — nếu muốn đóng góp test hồi quy thật, hãy ưu tiên thêm hàm `#[test]`.

### 4. Biên dịch Python Bindings
Nếu bạn muốn phát triển và kiểm tra tiện ích mở rộng Python tại máy cục bộ, bạn có thể biên dịch lại bằng Maturin. Trong môi trường ảo (virtual environment) của Python trên Windows PowerShell, hãy chạy lệnh:
```powershell
$env:PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1; .venv\Scripts\maturin.exe develop
```

### 5. Các chế độ nâng cao (Feature Flags)
Thư viện cung cấp các tùy chọn biên dịch linh hoạt:
- **Mặc định**: Sử dụng toàn bộ kho toán tử để đạt hiệu suất tìm kiếm tốt nhất.
- **Pure EML**: Chỉ sử dụng duy nhất toán tử EML cho mục đích nghiên cứu lý thuyết.
  ```bash
  cargo run --release --no-default-features
  ```

---
*Lưu ý: Thư viện `eml_sr` được tối ưu hóa cho hiệu suất cao, hãy luôn sử dụng chế độ `--release` để đạt tốc độ tốt nhất.*
