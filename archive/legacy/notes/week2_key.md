# MRDetect — Study Notes để làm rõ 3 Key Points
### Zviran et al., *Nat Med* 2020 — Genome-wide cfDNA mutational integration

> Mục tiêu: hiểu đủ sâu để *tự giải thích* và *bảo vệ* 3 key trước câu hỏi vặn.
> Cấu trúc: (A) 6 khái niệm nền bắt buộc → (B) chiều sâu riêng cho từng key.

---

# A. Sáu khái niệm nền — phải hiểu tới mức tự giải thích được

Nắm chắc 6 cái này thì 3 key tự bung ra.

## 1. Tumor fraction (TF) — trung tâm của mọi thứ
- TF = tỷ lệ ctDNA (DNA từ tumor) trong tổng cfDNA của plasma. **Không** phải "bao nhiêu mutation" mà là "bao nhiêu % phân tử DNA trôi nổi là của tumor".
- Di căn nặng: TF cao (vài %). MRD sau mổ: tumor bị cắt gần hết → TF tụt xuống 10⁻³, 10⁻⁴, thậm chí 10⁻⁵.
- Cảm giác con số: **TF = 10⁻⁵ nghĩa là cứ 100,000 phân tử DNA mới có 1 phân tử từ tumor.**
- TF quyết định mọi khó khăn phía sau.

## 2. Genomic equivalents (GEs) — khái niệm "trần"
- 1 GE = lượng DNA tương đương một bộ genome (một tế bào).
- Plasma chỉ có hữu hạn GEs: **median ~6,000 (range 400–14,000)** trong ~4.2 mL máu.
- **Số GE đặt một trần cứng lên depth hữu ích.** Chỉ có ~6,000 phân tử phân biệt tại một locus mà sequence 40,000X → phần dư chỉ là *đọc lại* cùng phân tử (PCR duplicate), không thêm thông tin.
- Ẩn dụ: "sequence sâu hơn = chụp cùng đám đông từ nhiều góc — vẫn bấy nhiêu người."
- ⟹ Đây là lý do **"depth" bị nghẽn**.

## 3. VAF ≠ TF — và vì sao VAF chết ở TF thấp
- VAF (variant allele fraction) = tỷ lệ read mang mutation tại *một* locus. Phương pháp cũ suy TF từ VAF.
- Ở TF = 10⁻⁵ với ~5,000 GE: tại một site kỳ vọng **0 hoặc 1** read mang mutation → VAF = 0 hoặc 1/coverage → **không informative**.
- MRDetect khác bản chất: không dùng VAF từng site, mà dùng **tỷ lệ số site detect được trên toàn genome** (`det_rate = M/R`).
- ⟹ Đây là lý do MRDetect **"orthogonal"** với mọi phương pháp cũ.

## 4. Hai quá trình lấy mẫu — KHÁI NIỆM QUAN TRỌNG NHẤT CẢ PAPER
Detect 1 SNV = hai phép lấy mẫu ngẫu nhiên nối tiếp:
- **Quá trình 1 (physical sampling):** phân tử mang mutation có *thật sự nằm trong* đám GEs được rút vào ống máu không? Ở TF thấp, xác suất này tự nó đã nhỏ.
- **Quá trình 2 (detection):** nếu có mặt, có đọc ra và tin được không?

Cả ngành 10 năm chỉ tối ưu Quá trình 2 (ultra-deep, error suppression).
**Đóng góp khái niệm của paper:** ở TF thấp, **Quá trình 1 mới là rào cản**. Không có phân tử vật lý ủng hộ mutation → sequence lý tưởng đến mấy cũng = 0.

> Nếu chỉ được nói một câu về paper, nói câu này. Cả Key 1 và Key 2 đều mọc ra từ đây.

## 5. Mô hình binomial — vì sao "nhiều site" cứu được tình thế
- Xác suất bắt ≥1 read cho *một* SNV ở TF=10⁻⁵ chỉ ~5%.
- Có **N site độc lập** → xác suất bắt ≥1 tín hiệu trên toàn bộ tăng nhanh theo N: `1 − (1−p)^N`.
- Với N = 10,000 site, dù mỗi site 5% thì tổng thể gần như chắc chắn detect được.
- Cốt lõi: **không cần bất kỳ site cụ thể nào chắc chắn — cần tập hợp lớn.** = "breadth supplants depth".
- Hiểu đúng: đây là *đánh đổi độ tin cậy per-site để lấy độ tin cậy tổng thể*, không phải phép màu.

## 6. Noise ở đây nghĩa là gì
- "Noise" = detection giả không đến từ tumor. Chủ yếu là **sequencing error (~1/1000 bp)**: máy đọc nhầm base thành đúng substitution đang tìm.
- Quét 10⁴ site × hàng triệu read → số lần "trùng khớp do lỗi" tích lũy đáng kể.
- Mấu chốt: ở TF ~10⁻⁵, **tín hiệu thật (1 read/site) và nhiễu có cùng độ lớn**.
- ⟹ Bài toán không phải "thấy mutation hay không" mà **"đám tín hiệu này có nhiều hơn đám nhiễu một cách có ý nghĩa không"** → dẫn thẳng vào Z-score.

---

# B. Chiều sâu cho từng key

## KEY 1 — MRDetect validate/xác định residual tumor như thế nào

Nắm **chuỗi 5 bước**, đặc biệt thấu **bước 3, 4, 5**.

### Bước 3 — vì sao "read-centric" chứ không "locus-centric"
- Mutation calling thường (MuTect, Strelka) là *locus-centric*: nhìn một vị trí, đếm nhiều read đồng thuận, dựng thống kê.
- Ở đây `TF << 1/depth` → mỗi site tốt nhất 1 read → **không có "nhiều read" để đồng thuận**.
- Đổi sang phân loại *từng read*: read này giống ctDNA thật hay artifact?
- SVM dùng 5 feature — hiểu **ý nghĩa vật lý**, không thuộc lòng:
  - **VBQ** (variant base quality): máy có tự tin về base sai lệch này không.
  - **MRBQ** (mean read base quality): chất lượng chung của read.
  - **PIR** (position in read): lỗi hay dồn về đầu 3' → vị trí mutation trong read là tín hiệu.
  - **R1/R2 concordance**: read forward/reverse overlap; cả hai cùng thấy → thật, chỉ một → nhiều khả năng lỗi.
  - **MQ** (mapping quality): aligner có tin read map đúng chỗ không.
- ⟹ Đây là **đổi mới khái niệm**, không chỉ là kỹ thuật lọc.

### Bước 4 — Noise model từ controls — CÂU TRẢ LỜI CHÍNH ⭐
- Lấy **chính compendium của bệnh nhân đó** áp lên plasma của **người không mang tumor này** (n=30 control).
- Mọi "detection" ở đây *theo định nghĩa* là nhiễu (những người này không thể có ctDNA của bệnh nhân).
- Từ đó tính **μ (trung bình), σ (độ lệch)** của tỷ lệ detection-do-nhiễu.
- Phải hiểu sâu: **noise tính riêng cho từng compendium**. Mỗi bộ mutation có "sequence-context" khác nhau (vd MSI nhiều mutation ở motif dễ lỗi) → error rate artifactual khác nhau.
- ⟹ **Không tồn tại một ngưỡng chung.** (Chỗ hay bị hỏi + chứng tỏ hiểu thật.)

### Bước 5 — Z-score = kiểm định giả thuyết ⭐
- `Z = (det_rate − μ) / σ` → tín hiệu bệnh nhân lệch *bao nhiêu độ lệch chuẩn* khỏi phân phối nhiễu.
- "Positive" = lệch đủ xa (vượt ngưỡng chọn theo specificity mong muốn).
- Diễn đạt được: **ta không hỏi "có mutation không", ta hỏi "đám tín hiệu này có nằm ngoài vùng mà chính bộ mutation đó tạo ra ngẫu nhiên trong plasma sạch không".** Đó chính là "validate residual tumor như thế nào".

### Tầng chồng bằng chứng (để ăn điểm)
Họ không tin một tín hiệu đơn lẻ — chồng bằng chứng độc lập:
- **SNV + CNA** (cơ chế nhiễu khác nhau, độc lập).
- **Cross-patient** specificity.
- **Copy-neutral** làm negative control.
- **Fragment size** ngắn hơn xác nhận sinh học.
- **Survival lâm sàng** (ground truth cuối).
> "Độ tin cậy đến từ hội tụ nhiều bằng chứng độc lập" = hiểu đúng tinh thần paper.

### Câu hỏi vặn thường gặp ở Key 1
- **"Z chỉ so control thì làm sao loại CHIP (đột biến từ tế bào máu)?"** → lọc riêng: gọi CNA/mutation trên PBMC vs normal, loại các event đó khỏi compendium (3 ca: LUAD10, LUAD26, CRC03).
- **"det_rate cao có thể do vài site nhiễu mạnh?"** → bootstrapping (down-sample 80%, n=20) xác nhận không do site cá biệt.

---

## KEY 2 — Vì sao không thể kết luận từ vài tumor reads

Là hệ quả của khái niệm nền 4 và 6. Trình bày được chuỗi:

1. Ở TF thấp, `TF << 1/depth` → tín hiệu thật tối đa = **1 read/site**.
2. Sequencing error ~1/1000 bp → quét 10⁴ site → nhiều read "trùng khớp mutation" chỉ do đọc sai.
3. Vậy 1 read thật và 1 read lỗi **trông giống hệt nhau** — vài reads nằm *trong* dải nhiễu, không phân biệt được.
4. Không dùng được "nhiều read đồng thuận tại 1 locus" (cách loại lỗi thông thường) vì *không đủ read*.
5. Thêm (Quá trình 1): fragment mang mutation có thể *không hề có mặt* trong ống → "không thấy" ≠ "không có bệnh".

**Kết luận dứt khoát:** "vài reads" là quan sát ở cấp đơn lẻ, mà ở cấp đơn lẻ thì tín hiệu và nhiễu không tách được. Chỉ khi tổng hợp toàn genome và so với phân phối nhiễu mới có phát biểu có ý nghĩa. → Key 2 dẫn thẳng vào Key 1.

**Điểm nâng tầm:** đây *không* phải "máy chưa đủ tốt". Ngay cả với sequencing hoàn hảo, error-free, exhaustive — Quá trình 1 (sampling) vẫn đặt trần. Rào cản **thống kê**, không phải **kỹ thuật**.

---

## KEY 3 — Thách thức chính

Phân biệt được **hai loại** (đừng gộp lẫn) = dấu hiệu hiểu sâu.

### Loại 1 — rào cản vật lý / thống kê (không thể "cố gắng hơn" mà vượt)
- **Trần cfDNA:** chỉ ~6,000 GE; đã *chứng minh* không cải thiện đáng kể bằng đổi kit extraction (test 4 kit). Dữ kiện, không phải phỏng đoán.
- **Sampling stochasticity:** bản chất ngẫu nhiên, không sửa bằng máy tốt hơn.
- **Error dominates** khi signal ≈ noise.

### Loại 2 — rào cản kỹ thuật / diễn giải (xử lý được nhưng phải cẩn thận)
- **Noise biến thiên per-compendium** → tính lại μ,σ mỗi bệnh nhân (không dùng ngưỡng cố định).
- **cfDNA vs gDNA khác coverage profile** (PCR-free vs PCR, chromatin/degradation) → phải xây plasma reference riêng cho CNA.
- **CHIP:** đột biến dòng máu giả làm tumor → lọc qua PBMC.
- **Ground truth mơ hồ:** vài ca post-op "detected" nhưng không tái phát. Là *khó khăn nội tại*, không hẳn lỗi phương pháp: adjuvant đã diệt? follow-up chưa đủ dài? true false positive? Không có cách phân định chắc chắn.

### Trade-off cốt lõi (câu chốt Key 3)
- MRDetect mạnh ở *detect có/không* nhưng **yếu ở định danh mutation cụ thể** (mỗi site độ tin cậy thấp).
- ⟹ **Bổ sung** chứ không **thay thế** deep targeted khi cần thông tin actionable (vd có nên dùng thuốc nhắm EGFR).
- Hiểu ranh giới ứng dụng này quan trọng hơn là chê/khen.

---

# Ba câu tự kiểm tra (trả lời trôi mà không nhìn slide = đủ)

1. **"Tại sao sequence sâu hơn không giải quyết được?"**
   → trần GE + Quá trình 1 (sampling), không chỉ "vì tốn kém".
2. **"Làm sao biết một detection là thật chứ không phải lỗi?"**
   → read-centric denoise → noise model từ control → Z-score → chồng bằng chứng orthogonal.
3. **"Nếu tốt vậy sao không thay hẳn deep targeted?"**
   → trade-off detect-vs-identify.
