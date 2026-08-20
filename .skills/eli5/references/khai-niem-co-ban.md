# Bộ analogy chuẩn cho các khái niệm cơ bản

Dùng NHẤT QUÁN các analogy này mỗi lần giải thích, để người dùng xây dựng được một "bản đồ tư duy" ổn định. Đây là hệ analogy trung tâm: **cơ thể = nhà hàng khổng lồ**.

## Hệ analogy trung tâm: quyển sách công thức

| Khái niệm | Analogy | Giải thích thêm |
|---|---|---|
| DNA | Quyển sách công thức nấu ăn gốc của cả nhà hàng, cất trong két sắt (nhân tế bào) | ~3 tỷ "ký tự", chỉ gồm 4 chữ cái A, T, G, C |
| Gene | Một công thức món ăn trong quyển sách | Người có ~20.000 công thức |
| RNA (mRNA) | Bản photocopy của MỘT công thức, mang xuống bếp dùng rồi vứt | Bản gốc không bao giờ rời két sắt |
| Phiên mã (transcription) | Hành động photocopy công thức | DNA → RNA |
| Protein | Món ăn nấu ra từ công thức | Thứ thật sự "làm việc" trong cơ thể |
| Dịch mã (translation) | Đầu bếp đọc bản photocopy và nấu món | RNA → protein |
| Gene expression (biểu hiện gene) | Công thức đó đang được photocopy NHIỀU hay ÍT | Đo bằng đếm số bản photocopy |
| Đột biến (mutation) | Lỗi đánh máy trong công thức | Có lỗi vô hại, có lỗi làm hỏng cả món ăn |
| Bộ gene (genome) | Toàn bộ quyển sách | Reference genome = quyển sách "mẫu chuẩn" của loài |
| Tế bào (cell) | Một gian bếp; mỗi gian bếp đều giữ nguyên một bản sao quyển sách | Bếp gan photocopy các công thức khác bếp da, dù sách giống nhau |

## Sequencing và dữ liệu — quy về tư duy dữ liệu

| Khái niệm | Cách giải thích cho dân CS/data |
|---|---|
| Sequencing (giải trình tự) | Máy "scan" các đoạn DNA/RNA thành file text. Nhưng máy chỉ đọc được từng mẩu ngắn (~100-150 ký tự), nên bạn nhận về hàng triệu mẩu vụn, như quyển sách bị cho vào máy hủy giấy |
| Read | Một mẩu vụn — một string ngắn A/T/G/C |
| FASTQ | File text thô từ máy: mỗi record 4 dòng (tên read, chuỗi ký tự, dấu +, điểm chất lượng từng ký tự). Đây là "raw data" |
| FASTA | Phiên bản gọn hơn: chỉ tên + chuỗi. Reference genome thường ở dạng này |
| Alignment (căn chỉnh) | Ghép từng mẩu vụn về đúng vị trí trong quyển sách mẫu — bản chất là fuzzy string matching một chuỗi ~100 ký tự vào chuỗi 3 tỷ ký tự. Tool: BWA, STAR, bowtie2 |
| BAM/SAM | File kết quả alignment: mỗi read + vị trí nó khớp trong genome. SAM là text, BAM là bản nén nhị phân |
| VCF | Bảng liệt kê các "lỗi đánh máy" (variant): tại vị trí X, sách mẫu ghi A nhưng mẫu của bệnh nhân ghi G |
| Count matrix (bảng đếm) | Bảng hàng = gene, cột = mẫu, ô = số read đếm được. Đây là điểm mà bioinformatics biến thành... data science bình thường: một cái dataframe |
| Coverage/depth | Trung bình mỗi vị trí trong sách được bao nhiêu mẩu vụn phủ lên. Depth thấp = kết luận không đáng tin |

## Các loại phân tích thường gặp

| Phân tích | Câu hỏi đời thường nó trả lời | Pipeline điển hình |
|---|---|---|
| RNA-seq / DE analysis | "Nhóm bếp bị bệnh photocopy công thức nào nhiều/ít hơn nhóm bếp khỏe?" | FASTQ → QC (FastQC) → align (STAR) hoặc pseudo-align (salmon) → count → DESeq2/edgeR → danh sách gene khác biệt |
| Variant calling | "Sách của bệnh nhân này có những lỗi đánh máy nào so với sách mẫu?" | FASTQ → align (BWA) → GATK → VCF |
| Single-cell RNA-seq | Như RNA-seq nhưng đo TỪNG gian bếp riêng lẻ thay vì trộn chung | CellRanger → Seurat/Scanpy → clustering → xác định loại tế bào |
| GWAS | "Lỗi đánh máy nào hay xuất hiện ở người mắc bệnh X?" — bản chất là chạy hàng triệu phép kiểm định thống kê |
| Phylogenetics | "Vẽ cây gia phả: các loài/chủng này họ hàng với nhau thế nào?" — so sánh độ giống nhau giữa các quyển sách |
| Enrichment / pathway analysis (GO, KEGG, GSEA) | "Danh sách gene tìm được có cùng thuộc một 'chương' nào trong sách không?" — ví dụ toàn công thức món tráng miệng → gợi ý cơ chế |
| BLAST | Google cho chuỗi sinh học: dán một chuỗi vào, tìm xem nó giống gene nào đã biết |

## Thống kê hay gặp

| Khái niệm | Giải thích |
|---|---|
| p-value & FDR/adjusted p-value | Khi kiểm định 20.000 gene cùng lúc, chắc chắn có gene "trông khác biệt" chỉ do may rủi. FDR là cách phạt để lọc bớt kết quả ăn may. Luôn dùng adjusted p-value, không dùng p-value thô |
| log2 fold change | Gene được photocopy nhiều gấp mấy lần. log2FC = 1 nghĩa là gấp đôi, = -1 là giảm một nửa |
| Normalization | Các mẫu được "scan" với độ sâu khác nhau, phải quy về cùng thang đo trước khi so sánh — như quy đổi tiền tệ trước khi so giá |

## Lưu ý khi dùng file này

- Đây là điểm khởi đầu, không phải giới hạn. Gặp khái niệm không có ở đây, tự tạo analogy mới theo cùng tinh thần (ưu tiên mở rộng hệ "nhà hàng/quyển sách" nếu khớp).
- Nếu người dùng làm mảng đặc thù (proteomics, metagenomics, cấu trúc protein...), xây bộ analogy riêng cho mảng đó nhưng vẫn neo vào hệ trung tâm khi được.