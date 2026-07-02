# Tình trạng Dự án & Phân tích Kỹ thuật

Tài liệu này cung cấp cái nhìn trung thực về những gì `eml_sr` có thể làm được hiện nay, hiệu năng thực đo được, và các hạn chế bạn cần biết trước khi dựa vào thư viện này. Tài liệu đã được viết lại để bỏ ngôn ngữ marketing mà các phiên bản trước chưa có đủ bằng chứng hỗ trợ.

## Tình trạng hiện tại (v0.2.2)

`eml_sr` là một engine hồi quy ký hiệu đang hoạt động và được phát triển tích cực. Nó **không** được xem là "sẵn sàng cho sản xuất" theo nghĩa có bộ test tự động, bộ benchmark đã kiểm chứng đầy đủ, hay xử lý lỗi đã được làm cứng — xem mục "Hạn chế đã biết" bên dưới. Những gì nó thực sự có là một thuật toán tìm kiếm hoạt động, đã kiểm chứng với các công thức thật:

- **Lớp bọc tìm kiếm thông minh Python (`SmartSearcher`)**: tầng biến đổi dữ liệu đầu ra ở mức Python, tìm kiếm trên các mục tiêu đã biến đổi ($y$, $y^2$, $\ln(y)$, $1/y$) để giải quyết các quan hệ phi tuyến mà engine gốc không thấy trực tiếp được.
- **Biên Pareto hợp nhất và Ánh xạ ngược**: chuyển các công thức ứng viên về hệ tọa độ gốc, tính lại MSE, điều chỉnh độ phức tạp theo hàm bọc ngoài, tạo biên Pareto thống nhất.
- **Chiến lược Ngắt Sớm**: ngắt tìm kiếm giữa các chiến lược ngay khi tìm được công thức khớp hoàn hảo (MSE gốc $< 10^{-15}$).
- **Lọc chùm tia Quality-Diversity (QD)**: giữ 80% ứng viên theo điểm số, 20% còn lại theo mức đa dạng cấu trúc, tránh đơn điệu hóa chùm tia.
- **Bảo vệ hội tụ Levenberg-Marquardt**: tự ngắt sớm nếu 3 vòng liên tiếp không cải thiện sai số hoặc $\lambda > 10^4$.
- **Toán tử tích hợp `Square` ($x^2$) và `Cube` ($x^3$)** để tiết kiệm độ sâu cây.
- **Tham số động Model-First**: hằng số là node tham số động (`Node::Param`), cho phép tối ưu đồng thời các hằng số lồng nhau.
- **Hồi quy đơn biến & đa biến**, **Khám phá Pareto-Front**, **Hỗ trợ đa nền tảng** (Windows x64, Linux x86_64, macOS Intel/Apple Silicon).

## EML thực sự đóng góp gì so với các toán tử "đường tắt"

Hãy đọc [README.md](../READMEVN.md#đọc-trước-khi-dùng-trạng-thái-thực-tế) trước nếu chưa đọc. Tóm lại: engine này là một thuật toán beam-search rời rạc kinh điển trên một bộ từ điển toán tử, trong đó EML chỉ là một thành viên. Trên thực tế, qua các công thức vật lý đã thử nghiệm, công thức tìm được gần như không bao giờ dùng trực tiếp toán tử `EML`, vì các đường tắt một/hai ngôi chuyên dụng (Exp, Log, Sqrt, Square, Divide...) rẻ hơn về số node dưới cách chấm điểm phạt theo độ phức tạp. EML chủ yếu có lợi cho các biểu thức dạng `eᴬ − ln(B)`.

Hai trường cấu hình `include_builtins` và `extra_operators` trong `SearchConfig` hiện **được khai báo nhưng không hề được đọc ở bất kỳ đâu trong engine tìm kiếm** (`run_bfs` luôn gọi cứng `OperatorRegistry::with_builtins()` bất kể config). Nếu bạn cần tùy biến bộ toán tử (ví dụ để ép tìm kiếm thiên về EML), hai trường này hiện chưa có tác dụng gì — đây là một khoảng trống đã biết, chưa phải tính năng được hỗ trợ.

## Tham chiếu Cấu hình Mặc định

- `max_complexity` : 6 - Độ sâu tối đa của cây biểu thức.
- `beam_width` : 200 - Số ứng viên giữ lại mỗi cấp độ (quan trọng cho RAM).
- `precision_goal` : 1e-10 - Ngưỡng sai số để dừng sớm.
- `complexity_penalty` : 0.1 - Hình phạt ưu tiên công thức đơn giản.
- `optimize_constants` : true - Bật tinh chỉnh hằng số độ chính xác cao.
- `alpha` : 0.0 - Hệ số phạt Elastic Net.
- `l1_ratio` : 0.5 - Tỷ lệ phạt L1/L2.

## Hiệu năng đo được (không phải số liệu quảng cáo)

- **Đánh giá từng ứng viên thực sự nhanh** (khoảng 1–1.5ms/ứng viên trên phần cứng thông thường), engine có thể sàng lọc hàng trăm nghìn ứng viên ở các cấp độ sâu — phần này của tuyên bố "engine Rust nhanh, song song" là thật và đo được.
- **Tổng thời gian chạy hết một lượt tìm kiếm KHÔNG nhanh** với các phương trình nhiều biến hoặc độ phức tạp cao. Trong quá trình tự kiểm thử với các công thức vật lý thật, một số phương trình đa biến (`max_complexity` 7–9, `beam_width` tới 1000) mất khoảng **hơn một giờ** để chạy xong trên một máy đơn. Đừng cho rằng tìm kiếm sẽ xong trong vài giây chỉ vì từng ứng viên được đánh giá nhanh — tổng số ứng viên ở các cấp độ sâu có thể rất lớn.
- Nếu cần kết quả nhanh, giữ `max_complexity` thấp (5–7) và `beam_width` vừa phải (200–500), chấp nhận đánh đổi độ đầy đủ lấy tốc độ.

## Hạn chế đã biết (ngoài an toàn bộ nhớ)

- **Không có bộ test tự động.** Không có bất kỳ hàm nào gắn `#[test]` trong `src/`, và CI (`.github/workflows/`) chỉ build và publish wheel — không chạy `cargo test`. Tính đúng đắn hiện chỉ được kiểm tra thủ công qua `cargo run --release` (các kịch bản demo trong `src/tests/mod.rs`) và `examples/`. Hãy thận trọng phù hợp với từng bản release cho tới khi việc này được khắc phục.
- **Không có bước đơn giản hóa đại số.** Tìm kiếm có thể trả về cấu trúc dư thừa (ví dụ một đẳng thức như `tan(arctan(x))` xuất hiện trong công thức lớn hơn) nếu nó tình cờ đạt điểm tốt; kết quả không đảm bảo ở dạng đơn giản nhất.
- **Các trường cấu hình `include_builtins` / `extra_operators` chưa có tác dụng** — như đã nêu ở trên.
- **Tính đúng của `to_python()`**: các bản build trước có lỗi thứ tự ưu tiên toán tử, trong đó `Neg`, `Inv`, `Divide` không tự bọc ngoặc riêng cho từng toán hạng trước khi ghép, nên khi lồng một biểu thức con `Plus`/`Subtract`/`Times` bên trong chúng (ví dụ làm mẫu số của phép chia), code Python xuất ra có thể âm thầm tính sai giá trị — dù việc đánh giá nội bộ bằng Rust và sai số báo cáo không bị ảnh hưởng. Lỗi này đã được sửa trong `src/ops/builtin.rs` (các toán hạng nay được bọc ngoặc riêng); nếu bạn đang dùng bản build cũ hơn, hãy kiểm tra lại bằng số trước khi tin tưởng code Python xuất ra trong pipeline khác.

---

## Hướng dẫn cho nhà phát triển

### 1. Biên dịch lại Python Bindings
```powershell
$env:PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1; .venv\Scripts\maturin.exe develop
```

### 2. Chạy bộ kiểm nghiệm demo
```bash
cargo run --release
```
Lệnh này chạy một số kịch bản viết tay trong `src/tests/mod.rs` và in ra kết quả kiểu pass/fail. Đây là kiểm tra thủ công, không phải bộ test hồi quy tự động (xem "Hạn chế đã biết" ở trên).

### 3. Chạy các ví dụ Rust
```bash
cargo run --release --example 01_simple_discovery
cargo run --release --example 02_multivariate
cargo run --release --example 03_constant_recognition
```

---

## ⚠️ Hạn chế Quan trọng & Cảnh báo An toàn

### 1. Quản lý Bộ nhớ (Cảnh báo về `beam_width`)
- **Cơ chế**: Ở mỗi cấp độ phức tạp, bộ tìm kiếm giữ lại `N` ứng viên tốt nhất (`N` = `beam_width`).
- **Rủi ro**: Đặt `beam_width` quá cao (5.000, 10.000+) trên máy RAM hạn chế sẽ khiến bộ nhớ bùng nổ theo cấp số nhân.
- **Khuyến nghị**: Bắt đầu với `beam_width` khoảng **200-500**.

### 2. Sự bùng nổ không gian tìm kiếm
- Tăng `max_complexity` làm số cấu trúc cây có thể có tăng theo cấp số nhân.
- **Mẹo**: Hầu hết định luật vật lý tìm được trong độ phức tạp **8-12**. Tăng cao hơn — theo số liệu đo ở trên — có thể biến thời gian chạy từ vài phút thành hơn một giờ.

### 3. Độ ổn định số học
- Cây biểu thức (đặc biệt cây pure-EML) có thể rất sâu, gây "catastrophic cancellation" hoặc tràn/dưới mức.
- **Cách xử lý**: dùng `allow_approximate: true` để bỏ qua nhánh không ổn định số học.

### 4. Sự hội tụ trong tối ưu hằng số
- Levenberg-Marquardt là bộ tối ưu cục bộ, có thể kẹt cực tiểu cục bộ nếu cấu trúc ban đầu quá xa thực tế.
