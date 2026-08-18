"""Modality-partitioned features and the A–F ablation grid.

The central question is whether methylation adds evidence **after** sequence and haplotype.
A design where features are one undifferentiated block cannot answer it, so features are
declared per modality and models are defined as *subsets of modalities*.

    Model   Sequence  Haplotype  Methylation
    A       yes       no         no            sequence-only baseline
    B       no        no         yes           methylation-only
    C       no        yes        no            haplotype-only
    D       yes       yes        no            the baseline to beat
    E       yes       no         yes           methylation without haplotype conditioning
    F       yes       yes        yes           the full proposal

The comparisons that decide the thesis are F−D, E−A and F−E
(``docs/research/04_evaluation_plan.md`` §1).

Leakage firewall
----------------
:data:`EVALUATION_ONLY_FIELDS` names the columns that must never become features.
:func:`build_feature_matrix` refuses to emit them, and ``tests/unit/test_leakage.py``
asserts that refusal. The check is by name rather than by convention because the field is
present in the same records the features are built from.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from ..joint_evidence.record import EVALUATION_ONLY_FIELDS, parse_float_list, parse_int_list

SEQUENCE = "sequence"
HAPLOTYPE = "haplotype"
METHYLATION = "methylation"
MODALITIES = (SEQUENCE, HAPLOTYPE, METHYLATION)


@dataclass(frozen=True)
class ModelSpec:
    """One cell of the ablation grid."""

    name: str
    modalities: Tuple[str, ...]
    role: str

    def uses(self, modality: str) -> bool:
        return modality in self.modalities


#: The six required ablations. Order matters only for reporting.
ABLATION_GRID: Dict[str, ModelSpec] = {
    "A": ModelSpec("A", (SEQUENCE,), "sequence-only baseline"),
    "B": ModelSpec("B", (METHYLATION,), "methylation-only"),
    "C": ModelSpec("C", (HAPLOTYPE,), "haplotype-only"),
    "D": ModelSpec("D", (SEQUENCE, HAPLOTYPE), "baseline to beat"),
    "E": ModelSpec("E", (SEQUENCE, METHYLATION), "methylation without haplotype conditioning"),
    "F": ModelSpec("F", (SEQUENCE, HAPLOTYPE, METHYLATION), "full proposal"),
}

#: The comparisons each hypothesis rests on, so a report cannot quietly omit one.
KEY_COMPARISONS = (
    ("F", "D", "does methylation add after sequence and haplotype? (H3 primary)"),
    ("E", "A", "does methylation add over sequence alone? (H3 secondary)"),
    ("D", "A", "does haplotype add over sequence alone? (is the baseline fair?)"),
    ("F", "E", "does haplotype *conditioning* matter? (earns the thesis title)"),
)


def sequence_features(row: Dict[str, str], candidate_alt: Optional[str] = None) -> Dict[str, float]:
    """Allele and alignment-quality evidence.

    ``supports_alt`` needs the candidate's ALT base. It is passed in rather than parsed
    from ``candidate_id`` inside a loop, so the caller controls the cost.
    """
    alt = candidate_alt if candidate_alt is not None else _alt_from_candidate_id(row.get("candidate_id", ""))
    observed = (row.get("observed_allele") or "").upper()
    return {
        "supports_alt": 1.0 if (alt and observed == alt.upper()) else 0.0,
        "allele_quality": _float(row.get("allele_quality")),
        "mapping_quality": _float(row.get("mapping_quality")),
        "read_length_kb": _float(row.get("read_length")) / 1000.0,
    }


def haplotype_features(row: Dict[str, str]) -> Dict[str, float]:
    """Phase context.

    ``haplotype_tag`` is encoded as an indicator, never as the raw integer: haplotype 1 and
    2 are labels whose orientation is arbitrary *within each phase set*, so treating them
    as an ordered numeric feature would invent a magnitude the data does not have.
    """
    haplotype = row.get("haplotype_tag")
    return {
        "is_haplotagged": 1.0 if haplotype not in (None, "") else 0.0,
        "haplotype_is_1": 1.0 if str(haplotype) == "1" else 0.0,
        "haplotype_is_2": 1.0 if str(haplotype) == "2" else 0.0,
        "has_phase_set": 1.0 if row.get("phase_set") not in (None, "") else 0.0,
    }


def methylation_features(row: Dict[str, str]) -> Dict[str, float]:
    """Native methylation evidence on this molecule.

    5mC and 5hmC are kept as separate features and never summed
    (``docs/research/05_claim_boundaries.md``). ``mean_distance_to_read_end`` is included so
    a model can express read-end unreliability rather than having it silently confounded in.
    """
    prob_5mc = parse_float_list(row.get("methylation_probabilities") or "")
    prob_5hmc = parse_float_list(row.get("methylation_probabilities_5hmc") or "")
    distances = parse_int_list(row.get("distance_of_cpgs_to_read_ends") or "")
    n_cpg = len(prob_5mc)

    methylated = _float(row.get("methylated_cpg_count"))
    unmethylated = _float(row.get("unmethylated_cpg_count"))
    confident = methylated + unmethylated

    return {
        "n_cpg": float(n_cpg),
        "mean_prob_5mc": _mean(prob_5mc),
        "mean_prob_5hmc": _mean(prob_5hmc),
        "methylated_fraction": (methylated / confident) if confident else 0.0,
        # How much of the read's methylation evidence was confident at all. A read of 100
        # ambiguous CpGs must not look like one of 100 confident ones.
        "confident_cpg_fraction": (confident / n_cpg) if n_cpg else 0.0,
        "mean_distance_to_read_end": _mean([float(d) for d in distances]),
    }


FEATURE_BUILDERS = {
    SEQUENCE: sequence_features,
    HAPLOTYPE: haplotype_features,
    METHYLATION: methylation_features,
}


def feature_names(spec: ModelSpec) -> List[str]:
    """Stable, sorted feature names for a model. Deterministic column order."""
    names: List[str] = []
    for modality in MODALITIES:
        if not spec.uses(modality):
            continue
        probe = FEATURE_BUILDERS[modality]({})
        names.extend(f"{modality}__{key}" for key in sorted(probe))
    return names


def build_feature_matrix(
    rows: Sequence[Dict[str, str]],
    spec: ModelSpec,
) -> Tuple[List[List[float]], List[str]]:
    """Build ``(matrix, feature_names)`` for one ablation model.

    Only the modalities in ``spec`` contribute. Evaluation-only columns are structurally
    unreachable: no builder reads them, and :func:`assert_no_evaluation_fields` re-checks
    the emitted names.
    """
    names = feature_names(spec)
    assert_no_evaluation_fields(names)

    matrix: List[List[float]] = []
    for row in rows:
        values: Dict[str, float] = {}
        for modality in MODALITIES:
            if not spec.uses(modality):
                continue
            built = FEATURE_BUILDERS[modality](row)
            values.update({f"{modality}__{k}": v for k, v in built.items()})
        matrix.append([values[name] for name in names])
    return matrix, names


def assert_no_evaluation_fields(names: Sequence[str]) -> None:
    """Raise if any feature name references an evaluation-only column.

    Named-based rather than type-based on purpose: the offending columns sit in the same
    record dicts the features come from, so only an explicit check catches a mistake.
    """
    offenders = [
        name
        for name in names
        if any(field in name for field in EVALUATION_ONLY_FIELDS)
    ]
    if offenders:
        raise ValueError(
            "evaluation-only fields must never become features: "
            + ", ".join(sorted(offenders))
            + " — see docs/research/05_claim_boundaries.md §2"
        )


def extract_labels(rows: Sequence[Dict[str, str]], positive_label: str = "tumor") -> List[int]:
    """Read evaluation-only labels into a 0/1 vector.

    Deliberately a separate function from feature building, called from evaluation code
    only, so that labels and features are never produced by one pass over the data.
    """
    return [1 if (row.get("source_label_for_evaluation_only") == positive_label) else 0 for row in rows]


def permute_methylation(rows: Sequence[Dict[str, str]], rng) -> List[Dict[str, str]]:
    """Shuffle methylation columns across rows — the capacity control for H3.

    Model F has more features than D, so some F−D gain is expected from capacity alone.
    Refitting F on permuted methylation measures that floor. Any real gain must exceed it
    (``docs/research/03_hypotheses.md`` H3 acceptance).
    """
    methylation_columns = [
        "cpg_positions",
        "methylation_probabilities",
        "methylation_probabilities_5hmc",
        "methylated_cpg_count",
        "unmethylated_cpg_count",
        "distance_of_cpgs_to_read_ends",
    ]
    order = list(range(len(rows)))
    rng.shuffle(order)
    permuted = []
    for target, source in enumerate(order):
        row = dict(rows[target])
        for column in methylation_columns:
            row[column] = rows[source].get(column, "")
        permuted.append(row)
    return permuted


def _alt_from_candidate_id(candidate_id: str) -> str:
    """``chr1:500:C>T`` → ``T``. Empty string when unparseable."""
    if ">" not in candidate_id:
        return ""
    return candidate_id.rsplit(">", 1)[1]


def _float(value) -> float:
    if value in (None, ""):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _mean(values: Sequence[float]) -> float:
    return (sum(values) / len(values)) if values else 0.0
