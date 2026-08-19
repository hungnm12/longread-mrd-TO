#!/usr/bin/env bash
# SNV-calling phase (tumor-only): run ClairS-TO on a tumor long-read BAM.
# STRICTLY tumor-only — no matched normal. SNV-only by default.
#
# Tool install / models / PoN databases are EXTERNAL dependencies (multi-GB, not
# vendored in this repo). Point to them via env vars (defaults below match the
# lab install). Nothing in src/ hard-codes these paths.
#
# Usage:
#   run_clairs_to.sh --tumor BAM --ref FASTA --outdir DIR [--platform P] [--threads N] [--region R]
set -euo pipefail

# ---- external dependency locations (override via env) ----
: "${CLAIRS_TO_DIR:=/big8_disk/hung114/ONT_MRD/week1/experiment/external/ClairS_TO_latest}"
: "${CLAIRS_TO_ENV:=/big8_disk/hung114/ONT_MRD/week1/experiment/resources/clairs_to_env}"  # conda-prefix-style dir with bin/clairs-to_models + bin/clairs-to_databases
: "${PYPY:=/big8_disk/hung114/ONT_MRD/week1/experiment/runtime/pypy3.10-v7.3.19-linux64/bin/pypy3}"
: "${LONGPHASE:=/big8_disk/hung114/ONT_MRD/week1/experiment/external/longphase_develop/longphase}"
: "${WHATSHAP:=$(command -v whatshap || true)}"
: "${PYTHON3:=$(command -v python3)}"
: "${SAMTOOLS:=$(command -v samtools)}"
: "${PARALLEL:=$(command -v parallel)}"

PLATFORM=ont_r10_dorado_sup_5khz_ssrs
THREADS=32
TUMOR="" ; REF="" ; OUTDIR="" ; REGION=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --tumor)   TUMOR="$2"; shift 2 ;;
    --ref)     REF="$2"; shift 2 ;;
    --outdir)  OUTDIR="$2"; shift 2 ;;
    --platform) PLATFORM="$2"; shift 2 ;;
    --threads) THREADS="$2"; shift 2 ;;
    --region)  REGION="$2"; shift 2 ;;
    *) echo "unknown arg $1" >&2; exit 2 ;;
  esac
done
[[ -n "$TUMOR" && -n "$REF" && -n "$OUTDIR" ]] || { echo "need --tumor --ref --outdir" >&2; exit 2; }
[[ -f "$TUMOR.bai" || -f "${TUMOR%.bam}.bai" ]] || "$SAMTOOLS" index "$TUMOR"
mkdir -p "$OUTDIR"

DB="$CLAIRS_TO_ENV/bin/clairs-to_databases"
PON="$DB/gnomad.r2.1.af-ge-0.001.sites.vcf.gz,$DB/dbsnp.b138.non-somatic.sites.vcf.gz,$DB/1000g-pon.sites.vcf.gz,$DB/CoLoRSdb.GRCh38.v1.1.0.deepvariant.glnexus.af-ge-0.001.vcf.gz"

# python shim: run_clairs_to has a `#!/usr/bin/env python` shebang
SHIM="$CLAIRS_TO_ENV/shim"; mkdir -p "$SHIM"; ln -sfn "$PYTHON3" "$SHIM/python"
export PATH="$SHIM:$PATH"

cmd=(
  "$PYTHON3" "$CLAIRS_TO_DIR/run_clairs_to"
  --tumor_bam_fn "$TUMOR" --ref_fn "$REF" --output_dir "$OUTDIR"
  --threads "$THREADS" --platform "$PLATFORM"
  --conda_prefix "$CLAIRS_TO_ENV" --panel_of_normals "$PON"
  --disable_indel_calling
  --python "$PYTHON3" --pypy "$PYPY" --samtools "$SAMTOOLS"
  --parallel "$PARALLEL" --whatshap "$WHATSHAP" --longphase "$LONGPHASE"
)
[[ -n "$REGION" ]] && cmd+=( --region "$REGION" )

{ "$SAMTOOLS" --version | head -1; echo "clairs_to_dir=$CLAIRS_TO_DIR"; echo "platform=$PLATFORM"; } > "$OUTDIR/tool_versions.txt"
echo "[run_clairs_to] tumor-only calling -> $OUTDIR (platform=$PLATFORM region=${REGION:-all})"
/usr/bin/time -v "${cmd[@]}" 2>&1 | tee "$OUTDIR/run.log"
echo "[run_clairs_to] done -> $OUTDIR/snv.vcf.gz"
