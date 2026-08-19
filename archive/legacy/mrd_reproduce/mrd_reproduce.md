# MRDetect — Reproduction Guide (weekend prototype)

*Mục tiêu thực tế cho tới thứ Hai: **hiểu method tới xương + môi trường sẵn sàng + một prototype lát-mỏng chạy được trên dữ liệu nhỏ + danh sách obstacles.** KHÔNG phải reproduce full WGS (bất khả thi trong 2 ngày). MRDetect không có code công khai (đã thành công ty C2i) → "reproduce" = tự implement từ paper.*

Đi kèm file: **`mrdetect_prototype.py`** — chạy `python mrdetect_prototype.py --demo` để thấy lõi hoạt động ngay, chưa cần data thật.

---

## 1. Thuật toán MRDetect (cái bạn đang implement)

Nguồn: Zviran et al., *Nature Medicine* 2020. Ý tưởng lõi: **"breadth thay depth"** — một site đơn ở TF cực thấp bị error nhấn chìm, nhưng **gộp bằng chứng qua hàng nghìn SNV somatic** thì tín hiệu u tách khỏi nền nhiễu.

Sáu bước:
1. **Tumor genotyping** — WGS tumor + matched normal → gọi somatic SNV → "compendium" đặc trưng bệnh nhân (hàng nghìn SNV).
2. **Plasma WGS** — giải trình tự plasma (hoặc **mô phỏng** bằng in-silico admixture ở TF thấp).
3. **Đếm tín hiệu từng site** — với mỗi SNV trong compendium, đếm read hỗ trợ alt (tumor allele) trong plasma.
4. **Khử nhiễu** — MRDetect dùng **SVM read-centric** để loại read giống-error, hạ error rate xuống ~5×10⁻⁵. *(Prototype: thay bằng lọc base-quality/mapping-quality đơn giản.)*
5. **Gộp tín hiệu (LÕI)** — cộng bằng chứng alt qua **tất cả** site → alt rate genome-wide tại các site tumor.
6. **Noise model + Z-score** — ước lượng nhiễu nền từ control plasma (TF=0), so tín hiệu quan sát với phân bố nhiễu → robust Z-score → phát hiện/không. Từ tín hiệu gộp cũng ước lượng được TF.

*(MRDetect còn tích hợp CNA; prototype bỏ qua, chỉ làm SNV.)*

---

## 2. Kế hoạch cuối tuần (theo thứ tự)

### Bước 0 — Hỏi Ping Ting NGAY (tiết kiệm nhiều ngày nhất)
- Lab server đã có sẵn **BAM tumor/normal** nào (cell line HCC1395/BL?) → khỏi tải từ đầu.
- Đã có sẵn **danh sách somatic SNV** nào chưa.
- Những **hố** cậu ấy vấp khi tái lập.

### Bước 1 — Hiểu method (vài giờ, làm đầu tiên)
Đọc kỹ Methods của MRDetect, viết lại 6 bước trên thành sơ đồ của bạn → đây là slide "Method".

### Bước 2 — Môi trường
```bash
# conda/mamba
mamba create -n mrd -c bioconda -c conda-forge \
    python=3.11 pysam samtools bcftools numpy scipy
mamba activate mrd
```
Dựng thẳng trên HPC/server lab (nơi có data + compute) nếu được.

### Bước 3 — Thu nhỏ về MỘT chromosome (mấu chốt để kịp cuối tuần)
Cả genome là bất khả thi trong 2 ngày. Cắt mọi thứ về `chr22` (hoặc chr20):
```bash
samtools view -b tumor.bam  chr22 > tumor.chr22.bam  && samtools index tumor.chr22.bam
samtools view -b normal.bam chr22 > normal.chr22.bam && samtools index normal.chr22.bam
```

### Bước 4 — Lấy danh sách somatic SNV (compendium)
- Nếu lab có sẵn → dùng luôn (lọc về chr22).
- Nếu chưa → gọi trên cặp cell line (giới hạn chr22). Nhanh gọn có thể dùng một somatic caller bất kỳ (ClairS-TO tumor-only, hoặc Mutect2/ClairS tumor-normal) → xuất VCF. Với prototype, danh sách "đủ dùng" là được, chưa cần hoàn hảo.

### Bước 5 — Mô phỏng plasma TF thấp (in-silico admixture)
Plasma = phần lớn DNA normal + một phần nhỏ TF là DNA tumor.
```bash
# Ví dụ TF ~ 1%: giữ ~1% read tumor, trộn với normal
samtools view -s 1.01 -b tumor.chr22.bam  > tumor.sub.bam   # 0.01 = 1%
samtools merge -f plasma_spiked.bam tumor.sub.bam normal.chr22.bam
samtools index plasma_spiked.bam
# Control TF=0: chỉ normal
cp normal.chr22.bam plasma_control.bam && samtools index plasma_control.bam
```
*(Số sau dấu chấm trong `-s SEED.FRAC` là tỉ lệ giữ lại. Kiểm TF thực tế đạt được bằng cách nhìn alt-fraction ở vài site clonal đã biết, rồi chỉnh.)*
Làm nhiều TF: 1%, 0.5%, 0.1% để vẽ đường độ nhạy.

### Bước 6 — Chạy prototype
```bash
python mrdetect_prototype.py \
    --snv-vcf tumor_somatic.chr22.vcf.gz \
    --plasma-bam plasma_spiked.bam \
    --control-bam plasma_control.bam \
    --chroms chr22
```
Ra: signal rate, noise mean, **Z-score**, ước lượng TF, detected/không.

### Bước 7 — Report thứ Hai (format Ping Ting)
- **Problem** — MRD là gì, vì sao TF thấp khó (error floor).
- **Method** — 6 bước MRDetect + sơ đồ của bạn.
- **Result** — kết quả prototype trên chr22 (dù chỉ là "tín hiệu gộp tách khỏi control ở TF ≥ X%"), + đường Z-score theo TF.
- **Obstacles** (phần Ping Ting nói quan trọng nhất) — xem mục 3.
- **Next steps** — hướng ONT.

---

## 3. Chỗ đơn giản hoá vs full MRDetect (đưa thẳng vào "Obstacles")

Đây là nội dung report có giá trị — chính là "chỗ không copy thẳng được":
- **Không có SVM khử nhiễu** — dùng lọc BQ/MAPQ đơn giản → error floor cao hơn bản gốc → detection limit kém hơn. (Bản gốc hạ error xuống ~5×10⁻⁵ nhờ SVM.)
- **Chỉ SNV, chưa CNA.**
- **Noise model đơn giản** (bootstrap theo site) thay cho mô hình đầy đủ của họ.
- **Chỉ 1 chromosome** → ít site hơn nhiều → độ nhạy thấp hơn (nhớ: độ nhạy tỉ lệ #sites × depth).
- **In-silico admixture** không mô phỏng artifact sinh học thật (fragmentomics, kích thước mảnh ctDNA...).
- **Không có code gốc** → mọi tham số/chi tiết phải suy từ paper (chỗ nào paper nói không rõ → ghi lại).

---

## 4. Nối sang hướng ONT (để đặt bối cảnh trong report)

Prototype này chạy trên logic short-read. Thesis là **mang nó sang ONT** — nơi **error rate cao hơn là bức tường trung tâm**. Hai lối vượt để nêu ở "Next steps":
- **Error model riêng cho ONT** (error phụ thuộc ngữ cảnh: homopolymer, k-mer) cho bước khử nhiễu.
- **Phased variants qua read dài** (kiểu PhasED-Seq, tận dụng LongPhase của lab) — yêu cầu nhiều đột biến đồng xuất hiện trên cùng molecule → đè false positive → biến read dài ONT thành *lợi thế* thay vì gánh nặng.

---

## 5. Kỳ vọng đúng
Cuối tuần = **hiểu sâu + prototype lõi trên chr22 + obstacles**, KHÔNG phải full WGS. Đó đã là một báo cáo tiến độ đáng nể, và đúng cái Ping Ting/thầy mong đợi.