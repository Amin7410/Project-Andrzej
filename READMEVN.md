[English click here!](README.md)

> [!IMPORTANT]
> **Phiên bản v0.2.2**
> Phiên bản này mang tới khung biến đổi dữ liệu đầu ra `SmartSearcher` (Identity, Square, Log, Inverse) để giải quyết các hàm phi tuyến, cơ chế tự động điều chỉnh beam_width và tối ưu hóa ngắt sớm (Early Stop). Đọc chi tiết tại tài liệu cập nhật của chúng tôi:
> - **v0.2.2**: [Các Cải tiến](docs/version_news/V0.2.2/improvements.md) | [Phân tích & Giải pháp](docs/version_news/V0.2.2/issues_and_solutions.md)
> - **v0.2.1**: [Các Cải tiến](docs/version_news/V0.2.1/improvements.md) | [Phân tích & Giải pháp](docs/version_news/V0.2.1/issues_and_solutions.md)
> - **v0.2.0**: [Các Cải tiến](docs/version_news/v0.2.0/improvements.md) | [Phân tích & Giải pháp](docs/version_news/v0.2.0/issues_and_solutions.md)

# eml_sr: Hồi quy Ký hiệu (Symbolic Regression) qua Toán tử EML

[![Crates.io](https://img.shields.io/crates/v/eml_sr.svg)](https://crates.io/crates/eml_sr)
[![PyPI](https://img.shields.io/pypi/v/eml-sr.svg)](https://pypi.org/project/eml-sr/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

| Hệ thống | Lệnh cài đặt nhanh | Kho lưu trữ |
| :--- | :--- | :--- |
| **Rust / Cargo** | `cargo add eml_sr` | [crates.io](https://crates.io/crates/eml_sr) |
| **Python / Pip** | `pip install eml_sr` | [pypi.org](https://pypi.org/project/eml-sr/) |

## Giới thiệu

**eml_sr** là một thư viện Rust cho bài toán hồi quy ký hiệu (symbolic regression) — tìm công thức toán học đóng khớp với một tập dữ liệu số. Không gian tìm kiếm của nó được xây dựng quanh **toán tử EML**, một phát hiện toán học có thật của Andrzej Odrzywołek (Đại học Jagiellonian):

```
eml(x, y) = e^x - ln(y)
```

Odrzywołek đã chứng minh rằng chỉ với toán tử nhị phân này và hằng số `1`, ta có thể dựng lại toàn bộ danh mục của một máy tính khoa học tiêu chuẩn — các phép toán số học, các hàm sơ cấp siêu việt, và các hằng số như e, π, i. Bài báo đã công bố trên arXiv: [*All elementary functions from a single binary operator*](https://arxiv.org/abs/2603.21852).

`eml_sr` dùng EML như một toán tử bên trong một engine hồi quy ký hiệu Rust thực dụng, cùng với các toán tử "đường tắt" thông thường (Sin, Cos, Exp, Log, Sqrt, Square, Cube, và các phép số học chuẩn). Xem mục **[Đọc trước khi dùng: Trạng thái thực tế](#đọc-trước-khi-dùng-trạng-thái-thực-tế)** bên dưới để biết chính xác cái gì đã cài đặt và cái gì vẫn chỉ là hướng nghiên cứu.

## Đọc trước khi dùng: Trạng thái thực tế

Mục này tồn tại vì các phiên bản README trước đây đã mô tả năng lực của dự án tự tin hơn nhiều so với những gì code hiện có thể làm. Vui lòng đọc kỹ trước khi quyết định dùng dự án này cho việc gì.

**Những gì đã cài đặt và hoạt động thật:**
- Một engine tìm kiếm theo chiều rộng (BFS) + beam search song song hóa bằng Rayon (`src/engine/bfs.rs`), duyệt qua các cây biểu thức tăng dần độ phức tạp, dựng từ EML cùng bộ toán tử tiêu chuẩn.
- Tối ưu cục bộ các hằng số bằng Levenberg–Marquardt (`src/engine/optimizer.rs`) — một kỹ thuật kinh điển, không phải thứ riêng có của EML.
- Một Pareto front các công thức đánh đổi giữa độ chính xác và độ phức tạp, cùng lớp bọc Python `SmartSearcher` (`smart_search.py`) thử tìm kiếm trên các target đã biến đổi (`y`, `y²`, `ln(y)`, `1/y`) để bắt được các hàm lồng trong `sqrt`/`log`/phép chia.
- API cho cả Rust và Python (qua PyO3), đã publish trên crates.io và PyPI. Phần này đã được kiểm thử với các công thức vật lý thật (một tập con của bộ benchmark Feynman) và tìm ra kết quả khớp chính xác hoặc gần chính xác cho nhiều công thức.

**Những gì CHƯA được cài đặt, dù các phiên bản tài liệu trước mô tả đây là ý tưởng cốt lõi của dự án:**
- **Tối ưu hóa gradient liên tục trên một cây EML "chủ" (master tree)** (huấn luyện một cây EML lớn bằng optimizer như Adam, rồi snap trọng số về 0/1 để lộ ra công thức) — đây là phương pháp được mô tả trong chính bài báo của Odrzywołek (và bài báo đó chỉ kiểm chứng ở độ sâu cây ≤ 4), và **đây không phải là cái mà engine Rust hiện tại đang làm**. Engine hiện tại là một thuật toán tìm kiếm tổ hợp rời rạc kiểu kinh điển, về bản chất tương tự các công cụ symbolic regression khác (như PySR, gplearn), với EML chỉ là một trong số các toán tử có sẵn.
- **Biên dịch công thức bất kỳ thành chuỗi lệnh EML thuần túy**, và bất kỳ **máy ảo EML / mạch analog / trình biên dịch VLSI** nào — đây là các *ứng dụng tiềm năng* của phần toán học nền tảng, được nêu ở mục dưới để có ngữ cảnh, không phải tính năng mà codebase này cung cấp.
- Trên thực tế, qua các công thức vật lý đã thử nghiệm, công thức tìm được gần như không bao giờ dùng trực tiếp toán tử `EML` — các toán tử "đường tắt" rẻ hơn (Exp, Log, Sqrt, Square, Divide...) luôn được ưu tiên bởi cách chấm điểm phạt theo độ phức tạp, vì chúng là toán tử một ngôi (unary) nên rẻ hơn về cấu trúc so với việc dựng lại cùng hàm đó qua EML. EML hiện chỉ thực sự có lợi cho các biểu thức đúng hình dạng `eᴬ − ln(B)` với A và B khác nhau.

Điều này không có nghĩa là nền tảng toán học sai — nó đã được kiểm chứng độc lập (xem trích dẫn ở trên). Nó có nghĩa là: khi cài `eml_sr` hôm nay, bạn nhận được một engine hồi quy ký hiệu Rust hoạt động tốt, kiểu kinh điển, có EML như một toán tử — chứ chưa phải là hiện thực hóa tầm nhìn "tối ưu hóa liên tục trên một toán tử vạn năng". Nếu bạn đang tìm cách tiếp cận dựa trên gradient đó, nó chưa tồn tại ở đây.

## Vì sao kết hợp EML với các toán tử tiêu chuẩn?

Một mình EML có thể biểu diễn mọi hàm sơ cấp, nhưng làm vậy có thể cần cây rất sâu (ví dụ dựng lại `sin(x)` chỉ từ các phép ghép `eml`), và chi phí tìm kiếm tăng theo cấp số nhân với độ sâu cây. Vì vậy mặc định `eml_sr` cũng đăng ký thêm các toán tử một/hai ngôi rẻ, chuyên dụng (Exp, Log, Sqrt, Sin, Cos, Tan, ArcSin/Cos/Tan, Square, Cube, và số học chuẩn) để việc tìm kiếm chạm tới các hàm phổ biến chỉ trong 1 node thay vì nhiều node. EML vẫn nằm trong bộ toán tử như một phương án dự phòng tổng quát — hữu ích nhất cho các quan hệ dạng `exp(...) − ln(...)` không có đường tắt riêng.

Nếu muốn ép tìm kiếm chỉ dùng EML (không có đường tắt), thư viện hỗ trợ chế độ build "Pure EML" ở compile-time — xem [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md). Lưu ý chế độ này làm tìm kiếm chậm và sâu hơn rất nhiều, như đã ghi trong [docs/STATUS.md](docs/STATUS.md).

## Cơ sở khoa học và Tác giả

**Andrzej Odrzywołek**, nhà vật lý lý thuyết tại Viện Vật lý Lý thuyết, Đại học Jagiellonian (Krakow, Ba Lan), đã tìm ra toán tử EML thông qua phương pháp tìm kiếm cạn kiệt có hệ thống, và chứng minh một cách xây dựng (constructive) rằng nó — kết hợp với hằng số 1 — đủ để tạo ra:
- Các phép tính số học cơ bản (+, -, ×, /).
- Tất cả các hàm số sơ cấp (sin, cos, log, lũy thừa...).
- Các hằng số nền tảng của toán học như e, π và đơn vị ảo i.

Tham khảo đầy đủ: [All elementary functions from a single binary operator, arXiv:2603.21852](https://arxiv.org/abs/2603.21852). Một bài báo tiếp theo của Tomasz Stachowiak, [*Algebraic structure behind Odrzywołek's EML operator*, arXiv:2604.23893](https://arxiv.org/abs/2604.23893), xem xét cấu trúc lý thuyết nhóm phía sau toán tử này. Dự án `eml_sr` là một nỗ lực kỹ thuật độc lập sử dụng toán tử EML; nó không do tác giả của hai bài báo trên viết hay chính thức liên kết với họ.

## Ứng dụng tiềm năng của EML (Khái niệm — chưa cài đặt trong dự án này)

Bản thân phần toán học mở ra nhiều hướng thú vị, được nêu dưới đây để có ngữ cảnh. **`eml_sr` hiện chưa cài đặt bất kỳ mục nào sau đây** — chúng được liệt kê để người đọc hiểu *vì sao* EML thú vị, không phải danh sách tính năng.

- **Phá vỡ "hộp đen" AI**: huấn luyện mạng nơ-ron trên cây EML bằng optimizer chuẩn rồi snap trọng số về giá trị chính xác (0 hoặc 1), về nguyên tắc có thể tạo ra công thức tường minh thay vì trọng số mờ. Đây là phương pháp đã được chứng minh (ở độ sâu nông) trong bài báo của Odrzywołek — không phải điều engine Rust này đang làm.
- **Trình biên dịch EML / Máy ngăn xếp một lệnh duy nhất**: vì mọi biểu thức hàm sơ cấp về nguyên tắc có thể viết lại thành chuỗi lệnh EML lồng nhau, người ta có thể biên dịch bất kỳ công thức nào thành một máy ngăn xếp "một lệnh" — hữu ích cho formal verification. Không có trình biên dịch như vậy trong repo này.
- **Thiết kế VLSI / Điện toán tương tự**: cấu trúc cây nhị phân đồng nhất của các đơn vị EML giống hệt nhau, về nguyên tắc có thể ánh xạ sang các phần tử mạch analog lặp lại thay vì thiết kế mạch riêng cho từng phép toán. Hoàn toàn là khái niệm ở đây.
- **Ngữ pháp tối giản để parse/lưu trữ**: ngữ pháp `S -> 1 | eml(S, S)` cực kỳ đơn giản, về nguyên tắc có thể đơn giản hóa việc lưu trữ/phân tích cú pháp biểu thức toán học. Cấu trúc dữ liệu nội bộ của `eml_sr` không dùng dạng tối giản này — nó dùng cây toán tử hỗn hợp, vì lý do hiệu năng đã giải thích ở trên.

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

Để biết thông tin chi tiết về khả năng hiện tại, nền tảng hỗ trợ, số liệu hiệu năng **đo được thật** (không phải số liệu quảng cáo), và cảnh báo an toàn về bộ nhớ, xem [docs/STATUS_VN.md](docs/STATUS_VN.md).

## Phát triển & Đóng góp

Nếu bạn muốn build từ mã nguồn, chạy benchmark, hoặc đóng góp vào nhân lõi, xem [docs/CONTRIBUTING_VN.md](docs/CONTRIBUTING_VN.md).

---
*Lưu ý: `eml_sr` là một engine hồi quy ký hiệu đang được phát triển tích cực và hoạt động thật. Nó chưa phải là hiện thực hóa đầy đủ tầm nhìn tối ưu hóa liên tục/huấn luyện gradient nêu ở trên — xem mục "Đọc trước khi dùng" để biết trạng thái trung thực hiện tại.*
