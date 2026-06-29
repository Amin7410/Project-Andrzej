# Hướng dẫn đóng góp cho eml_sr

Tài liệu này dành cho các nhà phát triển muốn biên dịch `eml_sr` từ mã nguồn, chạy thử nghiệm hoặc đóng góp vào dự án.

## Thiết lập Phát triển

### 1. Chạy bộ khung kiểm nghiệm (Demo)
Sau khi tải mã nguồn về, bạn có thể chạy ngay bộ khung kiểm nghiệm để thấy sức mạnh của toán tử EML trong việc tìm kiếm công thức:
```bash
cargo run --release
```

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

### 3. Tự thêm kịch bản kiểm tra của riêng bạn
Bạn có thể dễ dàng kiểm tra bất kỳ hàm số nào bằng cách mở file `src/tests/mod.rs` và thêm một `TestCase` mới vào hàm `get_test_suite()`. 
Mọi thay đổi sẽ tự động được cập nhật vào báo cáo khi bạn chạy `cargo run`.

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
