# eml_sr: Nguyên thủy hóa Toán học Liên tục trong Rust

[![Crates.io](https://img.shields.io/crates/v/eml_sr.svg)](https://crates.io/crates/eml_sr)
[![PyPI](https://img.shields.io/pypi/v/eml-sr.svg)](https://pypi.org/project/eml-sr/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

| Hệ thống | Lệnh cài đặt nhanh | Kho lưu trữ |
| :--- | :--- | :--- |
| **Rust / Cargo** | `cargo add eml_sr` | [crates.io](https://crates.io/crates/eml_sr) |
| **Python / Pip** | `pip install eml_sr` | [pypi.org](https://pypi.org/project/eml-sr/) |

## Giới thiệu
**eml_sr** là một thư viện Rust hiệu năng cao, hiện thực hóa một trong những khám phá cấu trúc sâu sắc nhất của toán học liên tục: **Toàn bộ các hàm số sơ cấp đều có thể được biểu diễn chỉ bằng một toán tử hai ngôi duy nhất.**

Trong thế giới điện tử kỹ thuật số, cổng NAND là viên gạch nền tảng để xây dựng mọi mạch logic phức tạp. Tương tự như vậy, **eml_sr** cung cấp một "cổng NAND cho toán học liên tục". Thư viện này cho phép các lập trình viên biên dịch mọi công thức phức tạp (từ số học cơ bản đến lượng giác, logarit, và hằng số siêu việt) thành một cấu trúc cây nhị phân đồng nhất tuyệt đối.

Thay vì phải duy trì một Cây Cú pháp Trừu tượng (AST) cồng kềnh với hàng chục loại Node khác nhau (Add, Sub, Sin, Cos, Exp), **eml_sr** thu gọn toàn bộ kiến trúc của bạn về đúng một loại Node duy nhất.

## Sự chuyển dịch Mô hình với EML

**eml_sr** không sinh ra để thay thế các thư viện tính toán chuẩn (Standard Math Libraries), mà nhằm cung cấp một cách tiếp cận hoàn toàn mới trong việc biểu diễn và khám phá cấu trúc toán học.

### 1. Chuyển đổi Cấu trúc Dữ liệu: Từ Đa dạng sang Đồng nhất
Khi xây dựng Cây cú pháp trừu tượng (AST) cho một biểu thức toán học:

*   **Phương pháp truyền thống (Heterogeneous AST)**: Sử dụng nhiều loại Node khác nhau (Add, Mul, Sin, Exp...).
    *   **Ưu điểm**: Mô tả trực tiếp và tính toán cực kỳ nhanh trên phần cứng hiện tại.
    *   **Thách thức**: Khi cần viết các thuật toán biến đổi công thức (như đạo hàm tự động, đơn giản hóa biểu thức), lập trình viên phải xử lý vô số trường hợp rẽ nhánh (switch-case) cho từng toán tử.

*   **Cách tiếp cận của EML (Homogeneous Binary Tree)**:
    Quy đổi toàn bộ không gian toán học về một loại Node duy nhất: `EmlNode`.
    *   **Giá trị mang lại**: Sự đa dạng của toán học được "nén" lại thành một cấu trúc đồ thị đồng nhất. Việc duyệt cây, phân tích cú pháp (parsing) hay biến đổi cấu trúc giờ đây chỉ cần một quy tắc đệ quy duy nhất. Code lõi của bạn trở nên siêu mỏng và cực kỳ an toàn.

### 2. Trí tuệ Nhân tạo (Symbolic Regression): Từ Tìm kiếm rời rạc sang Tối ưu hóa liên tục
Trong bài toán yêu cầu AI tự động tìm ra công thức từ dữ liệu thô:

*   **Phương pháp truyền thống (Combinatorial Search)**: AI phải chọn lựa và ghép nối từ một "từ điển" chứa hàng chục toán tử cơ sở (Base Set) khác nhau thông qua các thuật toán di truyền.
    *   **Đặc điểm**: Hiệu quả với các biểu thức ngắn, nhưng không gian tìm kiếm sẽ bùng nổ theo cấp số nhân khi độ phức tạp tăng lên.

*   **Cách tiếp cận của EML (Continuous Optimization)**:
    Bỏ qua hoàn toàn việc chọn hàm. AI được cung cấp một "Công thức chủ" (Master Formula) – một cây EML khổng lồ chứa mọi khả năng của hàm sơ cấp.
    *   **Giá trị mang lại**: EML biến bài toán "tìm kiếm tổ hợp" khó nhằn thành bài toán "tối ưu hóa Gradient" trơn tru. Bằng cách sử dụng các bộ tối ưu hóa chuẩn (như Adam) trên các nhánh cây và làm tròn trọng số (snapping), mạng Nơ-ron có thể tự động gọt giũa và làm lộ diện các định luật vật lý, toán học một cách rành mạch, giải quyết triệt để vấn đề "hộp đen" của AI.

> [!NOTE]
> **💡 Lưu ý về Kiến trúc & Đánh đổi (Trade-offs)**: Sự đồng nhất tuyệt đối của EML đi kèm với những đánh đổi về chiều sâu của cây biểu thức và yêu cầu khắt khe trong việc xử lý số phẩy động (Floating-point). Để hiểu rõ hơn về vấn đề này, hãy ghé xem bài phân tích và thảo luận của cá nhân tôi tại [WHATITHIN.txt](WHATITHINK.txt).

## Cơ sở khoa học và Tác giả

**Andrzej Odrzywołek**, nhà vật lý lý thuyết tại Viện Vật lý Lý thuyết thuộc Đại học Jagiellonian (Krakow, Ba Lan), là tác giả đứng sau phát hiện chấn động về tính tối giản của toán học liên tục. Thông qua nỗ lực nghiên cứu cá nhân và phương pháp tìm kiếm cạn kiệt có hệ thống, ông đã giải quyết được một bài toán mà trước đó chưa có tiền lệ: tìm ra một "nguyên tử" duy nhất cho mọi hàm số.

Khám phá cốt lõi của Andrzej Odrzywołek chính là toán tử EML (Exp-Minus-Log):
                $$eml(x, y) = \exp(x) - \ln(y)$$
Ông đã chứng minh một cách thuyết phục rằng toán tử này, khi kết hợp với duy nhất hằng số $1$, có thể tái tạo toàn bộ danh mục của một máy tính khoa học tiêu chuẩn. Điều này bao gồm:
- Các phép tính số học cơ bản ($+, -, \times, /$).
- Tất cả các hàm số sơ cấp (sin, cos, log, lũy thừa...).
- Các hằng số nền tảng của toán học như $e$, $\pi$ và đơn vị ảo $i$.

Tầm nhìn của Andrzej Odrzywołek không chỉ dừng lại ở lý thuyết thuần túy. Ông đã thiết lập một quy trình xác minh chặt chẽ, sử dụng các hằng số siêu việt độc lập để chứng minh rằng mọi biểu thức toán học đều có thể được chuyển đổi thành một cấu trúc cây nhị phân đồng nhất của các nút EML. Công trình của ông mở ra những ứng dụng tiềm năng to lớn trong việc tạo ra các mạch tính toán analog tối giản và thúc đẩy khả năng giải thích của trí tuệ nhân tạo thông qua hồi quy ký hiệu.

Tham khảo tài liệu đầy đủ tại đây: [All elementary functions from a single operator](https://www.alphaxiv.org/abs/2603.21852v2)

## Ứng dụng thực tế của EML

Sức mạnh của toán tử EML không chỉ nằm ở tính thanh lịch về mặt lý thuyết. Dưới đây là các lĩnh vực mà thư viện `eml_sr` có thể trở thành nhân lõi cho những hệ thống phần mềm thế hệ mới.

### 1. Công cụ Trí tuệ Nhân tạo (Machine Learning & Symbolic Regression)

Đây là ứng dụng lớn nhất và thực tế nhất của EML trong phần mềm hiện nay:

- **Hồi quy Ký hiệu (Symbolic Regression)**: Thay vì các mô hình AI tìm kiếm trên những ngữ pháp hỗn tạp chứa nhiều toán tử khác nhau, EML cho phép tạo ra một "công thức chủ" (master formula) đa tham số bằng cấu trúc cây nhị phân. Toàn bộ không gian tìm kiếm được thu gọn về việc tối ưu hóa trọng số trên một cấu trúc đồng nhất duy nhất, thay vì phải dò dẫm qua hàng tỷ tổ hợp cấu trúc khác nhau.

- **Phá vỡ "Hộp đen" AI**: Bạn có thể dùng các thuật toán tối ưu hóa chuẩn (như Adam) để huấn luyện mạng nơ-ron dựa trên cây EML này. Khi huấn luyện thành công, hệ thống có thể ép các trọng số về các giá trị chính xác (0 hoặc 1), giúp AI xuất ra hẳn một **công thức toán học tường minh** (closed-form expressions) thay vì chỉ là các con số dự đoán. Đây chính là chìa khóa để biến AI từ một "hộp đen" thành một công cụ mà con người có thể đọc, hiểu và tin tưởng.

### 2. Xây dựng Trình biên dịch (Compilers) và Máy ảo (Virtual Machines)

EML cung cấp một nền tảng lý tưởng để các nhà phát triển xây dựng các hệ thống thực thi siêu tối giản:

- **Trình biên dịch EML**: Bạn có thể dùng thư viện `eml_sr` làm nhân lõi để viết các phần mềm trình biên dịch có khả năng chuyển đổi bất kỳ công thức toán học nào (ví dụ: $\sin(x) + e^x$) thành dạng EML thuần túy — một chuỗi các lệnh EML lồng nhau chỉ chứa hằng số $1$.

- **Máy ảo một tập lệnh (Single Instruction Stack Machine)**: Dạng EML thuần túy này có thể được thực thi trên phần mềm giả lập một cỗ máy ngăn xếp chỉ có đúng một tập lệnh duy nhất. Hãy tưởng tượng một chiếc máy tính RPN (Reverse Polish Notation) chỉ có đúng một nút bấm — đó chính là bản chất của máy ảo EML. Sự đơn giản cực độ này giúp việc xác minh tính đúng đắn (formal verification) trở nên khả thi và dễ dàng hơn bao giờ hết.

### 3. Phần mềm Thiết kế Vi mạch và Tính toán Analog

EML làm cầu nối giữa kỹ sư phần mềm và kỹ sư phần cứng:

- Bởi vì mọi hàm sơ cấp đều trở thành các cây nhị phân đồng nhất trong ký pháp EML, bạn có thể dùng thư viện `eml_sr` để viết phần mềm biên dịch công thức thành các **bản thiết kế mạch điện** (circuit schematics).

- Điều này rất hữu ích cho lĩnh vực **điện toán tương tự** (analog computing), nơi các kỹ sư có thể tạo ra các mạch tính toán hàm đa biến bằng cách ghép nối một cấu trúc topology cây nhị phân của các phần tử EML giống hệt nhau. Thay vì phải thiết kế riêng từng mạch cho mỗi phép toán ($+$, $\times$, $\sin$...), bạn chỉ cần sản xuất hàng loạt một loại linh kiện EML duy nhất và kết nối chúng theo sơ đồ cây.

### 4. Thiết kế Cấu trúc Dữ liệu và Phân tích Cú pháp (Parsing)

EML mang lại sự đơn giản triệt để cho việc xử lý biểu thức toán học trong phần mềm:

- Thay vì phải viết code xử lý cho hàng chục phép toán khác nhau ($+, -, \sin, \cos...$), phần mềm của bạn chỉ cần xử lý một **ngữ pháp phi ngữ cảnh cực kỳ đơn giản**:
$$S \rightarrow 1 \mid eml(S, S)$$

- Điều này giúp các hệ thống lưu trữ, phân tích cú pháp (parser) hoặc xử lý hình thức các biểu thức toán học trở nên vô cùng đồng nhất. Mọi biểu thức — dù phức tạp đến đâu — đều được biểu diễn bằng cùng một cấu trúc dữ liệu, cùng một thuật toán duyệt cây, và cùng một logic đánh giá. Không còn ngoại lệ, không còn rẽ nhánh đặc biệt.

## Hướng dẫn sử dụng

Dự án được thiết kế để phục vụ cả mục đích nghiên cứu lý thuyết lẫn ứng dụng thực tế.

### 1. Chạy bộ khung kiểm nghiệm (Demo)
Sau khi tải mã nguồn về, bạn có thể chạy ngay bộ khung kiểm nghiệm để thấy sức mạnh của toán tử EML trong việc tìm kiếm công thức:
```bash
cargo run
```

### 2. Xem các ví dụ mẫu sinh động
Chúng tôi cung cấp thư mục `examples/` để bạn học cách sử dụng qua thực tế. Hãy thử chạy các lệnh sau:
```bash
# Tìm hàm đơn biến
cargo run --example 01_simple_discovery

# Tìm hàm đa biến
cargo run --example 02_multivariate

# Nhận diện hằng số toán học
cargo run --example 03_constant_recognition
```

### 3. Tự thêm kịch bản kiểm tra của riêng bạn
Bạn có thể dễ dàng kiểm tra bất kỳ hàm số nào bằng cách mở file `src/tests/mod.rs` và thêm một `TestCase` mới vào hàm `get_test_suite()`. 
Mọi thay đổi sẽ tự động được cập nhật vào báo cáo khi bạn chạy `cargo run`.

### 3. Tích hợp EML-SR vào dự án của bạn
Nếu bạn đang xây dựng một ứng dụng khác và muốn sử dụng "bộ não" của `eml_sr`, hãy thêm vào `Cargo.toml`:
```toml
[dependencies]
eml_sr = { git = "https://github.com/Amin7410/Project-Andrzej.git" }
```

Và sử dụng trong mã nguồn:
```rust
use eml_sr::{Searcher, SearchConfig};

fn main() {
    let config = SearchConfig::default();
    let searcher = Searcher::new(config);
    
    // Tìm kiếm công thức từ dữ liệu x, y của bạn
    // let result = searcher.find_function(&xs, &ys);
}
```

### 4. Các chế độ nâng cao (Feature Flags)
Thư viện cung cấp các tùy chọn biên dịch linh hoạt:
- **Mặc định**: Sử dụng toàn bộ kho toán tử để đạt hiệu suất tìm kiếm tốt nhất.
- **Pure EML**: Chỉ sử dụng duy nhất toán tử EML cho mục đích nghiên cứu lý thuyết.
  ```bash
  cargo run --no-default-features
  ```

---
*Lưu ý: Thư viện `eml_sr` được tối ưu hóa cho hiệu suất cao, khuyến khích chạy ở chế độ `--release` để đạt tốc độ tốt nhất.*