### Setup (dựng công cụ, chưa ra kết luận):

Viết tiêu chí "đạt" bằng con số: ngưỡng precision/recall/F1 cho caller, LoD mục tiêu, khoảng kích thước compendium kỳ vọng theo loại ung thư.

Tải + validate truth-set (COLO829/HCC1395): truth VCF, HC-region BED, reads/BAM long-read. Đếm để chắc lấy đúng file.
Dựng harness tái lập được, pin version.

### Thí nghiệm A — validate caller (chứng minh pipeline dựng compendium tin được):
4. Chạy ClairS-TO tumor-only (chỉ feed tumor reads) trên truth sample.
5. So với truth trong HC regions bằng som.py/vcfeval → precision / recall / F1.
6. Đối chiếu với con số published của chính caller.

### Thí nghiệm B — validate detection (dùng mixed BAM 1% / 0.1% / 0.01%):
7. Ghép: compendium (danh sách mutation đã biết) + ladder pha loãng + một control 0% (normal-only) — bắt buộc.
8. Score từng BAM tại vị trí compendium, tích hợp tín hiệu toàn genome (kèm khử nhiễu), tính detection score so với control.
9. Vẽ đường titration, xác định LoD, gọi detected/not-detected ở từng mức.
10. So LoD với paper (họ tới 10⁻⁵).