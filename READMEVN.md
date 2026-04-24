# eml_sr: Nguyên thủy hóa Toán học Liên tục trong Rust

[![Crates.io](https://img.shields.io/crates/v/eml_sr.svg)](https://crates.io/crates/eml_sr)
[![PyPI](https://img.shields.io/pypi/v/eml-sr.svg)](https://pypi.org/project/eml-sr/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

| Hệ thống | Lệnh cài đặt nhanh | Kho lưu trữ |
| :--- | :--- | :--- |
| **Rust / Cargo** | `cargo add eml_sr` | [crates.io](https://crates.io/crates/eml_sr) |
| **Python / Pip** | `pip install eml_sr` | [pypi.org](https://pypi.org/project/eml-sr/) |

## Giới thiệu
**eml_sr** là một thư viện Rust hiệu năng cao, được xây dựng dựa trên một trong những khám phá cấu trúc sâu sắc nhất của toán học liên tục: **Toàn bộ các hàm số sơ cấp đều có thể được biểu diễn bằng toán tử EML.**

Trong thế giới điện tử kỹ thuật số, cổng NAND là viên gạch nền tảng. Tương tự như vậy, **eml_sr** cung cấp "toán tử EML" như một cầu nối vạn năng cho toán học liên tục. Thư viện này cho phép các lập trình viên biểu diễn mọi công thức phức tạp bằng một cấu trúc EML đồng nhất hoặc một cấu trúc kết hợp (hybrid) hiệu năng cao giữa EML và các toán tử tiêu chuẩn đã được tối ưu.

Thay vì phụ thuộc hoàn toàn vào các Cây Cú pháp Trừu tượng (AST) cồng kềnh và rời rạc, **eml_sr** mang đến sức mạnh giúp bạn tinh gọn kiến trúc toán học bằng cách lấy EML làm nhân lõi hợp nhất.

## Sự chuyển dịch Mô hình với EML

**eml_sr** không sinh ra để thay thế các thư viện tính toán chuẩn (Standard Math Libraries), mà nhằm cung cấp một cách tiếp cận hoàn toàn mới trong việc biểu diễn và khám phá cấu trúc toán học.

### 1. Chuyển đổi Cấu trúc Dữ liệu: Từ Đa dạng sang Đồng nhất
Khi xây dựng Cây cú pháp trừu tượng (AST) cho một biểu thức toán học:

*   **Phương pháp truyền thống (Heterogeneous AST)**: Sử dụng nhiều loại Node khác nhau (Add, Mul, Sin, Exp...).
    *   **Ưu điểm**: Mô tả trực tiếp và tính toán cực kỳ nhanh trên phần cứng hiện tại.
    *   **Thách thức**: Khi cần viết các thuật toán biến đổi công thức (như đạo hàm tự động, đơn giản hóa biểu thức), lập trình viên phải xử lý vô số trường hợp rẽ nhánh (switch-case) cho từng toán tử.

*   **Cách tiếp cận của EML (Homogeneous Binary Tree)**:
    Giảm thiểu độ phức tạp của không gian toán học bằng cách sử dụng `EmlNode` làm cấu trúc hợp nhất.
    *   **Giá trị mang lại**: Sự đa dạng của toán học được "nén" lại thành một cấu trúc đồ thị tinh gọn. Dù sử dụng EML thuần túy hay các mô hình kết hợp (hybrid) tối ưu, mã nguồn lõi của bạn vẫn luôn tinh giản, dễ đoán và cực kỳ an toàn.

### 2. Trí tuệ Nhân tạo (Symbolic Regression): Từ Tìm kiếm rời rạc sang Tối ưu hóa liên tục
Trong bài toán yêu cầu AI tự động tìm ra công thức từ dữ liệu thô:

*   **Phương pháp truyền thống (Combinatorial Search)**: AI phải chọn lựa và ghép nối từ một "từ điển" chứa hàng chục toán tử cơ sở (Base Set) khác nhau thông qua các thuật toán di truyền.
    *   **Đặc điểm**: Hiệu quả với các biểu thức ngắn, nhưng không gian tìm kiếm sẽ bùng nổ theo cấp số nhân khi độ phức tạp tăng lên.

*   **Cách tiếp cận của EML (Continuous Optimization)**:
    Bỏ qua hoàn toàn việc chọn hàm. AI được cung cấp một "Công thức chủ" (Master Formula) – một cây EML khổng lồ chứa mọi khả năng của hàm sơ cấp.
    *   **Giá trị mang lại**: EML biến bài toán "tìm kiếm tổ hợp" khó nhằn thành bài toán "tối ưu hóa Gradient" trơn tru. Bằng cách sử dụng các bộ tối ưu hóa chuẩn (như Adam) trên các nhánh cây và làm tròn trọng số (snapping), mạng Nơ-ron có thể tự động gọt giũa và làm lộ diện các định luật vật lý, toán học một cách rành mạch, giải quyết triệt để vấn đề "hộp đen" của AI.

### 3. EML: Sự hiệu quả kết hợp với Tính vạn năng

Để hiểu được giá trị độc bản của **eml_sr**, hãy hình dung mối quan hệ giữa các Toán tử thông thường và Toán tử EML:

*   **Toán tử thông thường (Sin, Cos, Pi, E...) giống như "Linh kiện đúc sẵn"**: Chúng là những thành phần đã có hình dáng cố định. Nếu bạn muốn xây một ngôi nhà tiêu chuẩn, việc sử dụng các linh kiện này sẽ cực kỳ nhanh chóng và hiệu quả. Đây chính là những "Đường tắt tốc độ cao" của chúng ta để tìm ra các định luật toán học đã biết.
*   **Toán tử EML giống như "Đất sét"**: Bạn có thể nặn đất sét thành *bất kỳ* hình thù nào. Dù bạn có thể dùng đất sét để nặn ra một viên gạch, nhưng sức mạnh thực sự của nó nằm ở việc tạo ra những hình khối hữu cơ, phức tạp mà không một viên gạch đúc sẵn nào có thể biểu diễn được.

Trong **eml_sr**, chúng tôi kết hợp cả hai. Chúng tôi cung cấp các hằng số và hàm số tiêu chuẩn để đảm bảo bộ máy chạy nhanh như chớp cho các tác vụ thông thường. Nhưng chúng tôi luôn giữ **EML làm nhân lõi** để đảm bảo bộ máy không bao giờ bị giới hạn. Khi toán học truyền thống gặp bế tắc trước một mối quan hệ mới lạ, EML sẽ đóng vai trò là công cụ khám phá vạn năng để tìm ra những định luật thậm chí còn chưa có tên gọi.


> [!NOTE]
> **💡 Lưu ý về Kiến trúc & Đánh đổi (Trade-offs)**: Sự đồng nhất tuyệt đối của EML đi kèm với những đánh đổi về chiều sâu của cây biểu thức và yêu cầu khắt khe trong việc xử lý số phẩy động (Floating-point). Để hiểu rõ hơn về vấn đề này, hãy ghé xem bài phân tích và thảo luận của cá nhân tôi tại [docs/WHATITHINK.txt](docs/WHATITHINK.txt).

## Cơ sở khoa học và Tác giả

**Andrzej Odrzywołek**, nhà vật lý lý thuyết tại Viện Vật lý Lý thuyết thuộc Đại học Jagiellonian (Krakow, Ba Lan), là tác giả đứng sau phát hiện chấn động về tính tối giản của toán học liên tục. Thông qua nỗ lực nghiên cứu cá nhân và phương pháp tìm kiếm cạn kiệt có hệ thống, ông đã giải quyết được một bài toán mà trước đó chưa có tiền lệ: tìm ra một "nguyên tử" duy nhất cho mọi hàm số.

Khám phá cốt lõi của Andrzej Odrzywołek chính là toán tử EML (Exp-Minus-Log):
                eml(x, y) = e^(x) - ln(y)
Ông đã chứng minh một cách thuyết phục rằng toán tử này, khi kết hợp với duy nhất hằng số 1, có thể tái tạo toàn bộ danh mục của một máy tính khoa học tiêu chuẩn. Điều này bao gồm:
- Các phép tính số học cơ bản (+, -, x, /).
- Tất cả các hàm số sơ cấp (sin, cos, log, lũy thừa...).
- Các hằng số nền tảng của toán học như e, pi và đơn vị ảo i.

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

- **Trình biên dịch EML**: Bạn có thể dùng thư viện `eml_sr` làm nhân lõi để viết các phần mềm trình biên dịch có khả năng chuyển đổi bất kỳ công thức toán học nào (ví dụ: sin(x) + e^x) thành dạng EML thuần túy — một chuỗi các lệnh EML lồng nhau chỉ chứa hằng số 1.

- **Máy ảo một tập lệnh (Single Instruction Stack Machine)**: Dạng EML thuần túy này có thể được thực thi trên phần mềm giả lập một cỗ máy ngăn xếp chỉ có đúng một tập lệnh duy nhất. Hãy tưởng tượng một chiếc máy tính RPN (Reverse Polish Notation) chỉ có đúng một nút bấm — đó chính là bản chất của máy ảo EML. Sự đơn giản cực độ này giúp việc xác minh tính đúng đắn (formal verification) trở nên khả thi và dễ dàng hơn bao giờ hết.

### 3. Phần mềm Thiết kế Vi mạch và Tính toán Analog

EML làm cầu nối giữa kỹ sư phần mềm và kỹ sư phần cứng:

- Bởi vì mọi hàm sơ cấp đều trở thành các cây nhị phân đồng nhất trong ký pháp EML, bạn có thể dùng thư viện `eml_sr` để viết phần mềm biên dịch công thức thành các **bản thiết kế mạch điện** (circuit schematics).

- Điều này rất hữu ích cho lĩnh vực **điện toán tương tự** (analog computing), nơi các kỹ sư có thể tạo ra các mạch tính toán hàm đa biến bằng cách ghép nối một cấu trúc topology cây nhị phân của các phần tử EML giống hệt nhau. Thay vì phải thiết kế riêng từng mạch cho mỗi phép toán (+, x, sin...), bạn chỉ cần sản xuất hàng loạt một loại linh kiện EML duy nhất và kết nối chúng theo sơ đồ cây.

### 4. Thiết kế Cấu trúc Dữ liệu và Phân tích Cú pháp (Parsing)

EML mang lại sự đơn giản triệt để cho việc xử lý biểu thức toán học trong phần mềm:

- Thay vì phải viết code xử lý cho hàng chục phép toán khác nhau (+, -, sin, cos...), phần mềm của bạn chỉ cần xử lý một **ngữ pháp phi ngữ cảnh cực kỳ đơn giản**: S -> 1|eml(S, S)

- Điều này giúp các hệ thống lưu trữ, phân tích cú pháp (parser) hoặc xử lý hình thức các biểu thức toán học trở nên vô cùng hiệu quả. Mọi biểu thức — dù phức tạp đến đâu — đều có thể được quy đổi về một cấu trúc đồng nhất, giúp đơn giản hóa logic đánh giá và giảm bớt gánh nặng về mặt kiến trúc.

## Bắt đầu nhanh

### 1. Cài đặt

**Dành cho người dùng Python:**
```bash
pip install eml_sr
```

**Dành cho người dùng Rust:**
```bash
cargo add eml_sr
```

### 2. Cách dùng cơ bản (Python)

Khám phá công thức ẩn trong dữ liệu của bạn bằng API tương thích với Scikit-Learn:

```python
from eml_sr import Searcher

# Dữ liệu của bạn
X = [[1.0], [2.0], [3.0]]
y = [2.5, 4.5, 6.5]  # f(x) = 2x + 0.5

# Tìm kiếm công thức
searcher = Searcher()
result = searcher.fit(X, y)

print(f"Công thức tìm được: {result.formula}")
# Kết quả: Công thức tìm được: (v_{0} * 2.0) + 0.5
```

### 3. Cách dùng cơ bản (Rust)

```rust
use eml_sr::{Searcher, SearchConfig};

fn main() {
    let searcher = Searcher::new(SearchConfig::default());
    let xs = vec![1.0, 2.0, 3.0];
    let ys = vec![2.5, 4.5, 6.5];
    
    if let Ok(result) = searcher.find_function(&xs, &ys) {
        println!("Tìm thấy công thức: {}", result.formula);
    }
}
```

## Tình trạng Dự án & An toàn

Để biết thông tin chi tiết về khả năng hiện tại, các nền tảng hỗ trợ và **cảnh báo an toàn quan trọng** về việc sử dụng bộ nhớ (OOM), vui lòng xem [docs/STATUS_VN.md](docs/STATUS_VN.md).

## Phát triển & Đóng góp

Nếu bạn muốn biên dịch từ mã nguồn, chạy thử nghiệm hiệu năng, hoặc đóng góp vào nhân lõi của bộ máy, vui lòng xem tài liệu [docs/CONTRIBUTING_VN.md](docs/CONTRIBUTING_VN.md).

---
*Lưu ý: Thư viện `eml_sr` là một bản hiện thực hóa sẵn sàng cho sản xuất của lý thuyết toán tử EML.*
