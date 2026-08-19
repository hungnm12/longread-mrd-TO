"""Joint-molecule evidence: allele + haplotype + native methylation on one read.

The data contract is ``docs/joint_molecule_schema.md``. ``labels`` is deliberately **not**
re-exported here — it is evaluation-only, and importing it should be a conscious act.
"""
from .extract import Candidate, ExtractionConfig, extract_region, iter_candidates_from_tsv
from .record import (
    EVALUATION_ONLY_FIELDS,
    FIELDS,
    SCHEMA_VERSION,
    ExclusionReason,
    JointMoleculeRecord,
)
from .writer import JointEvidenceStore, describe_inputs, input_manifest_id

__all__ = [
    "Candidate",
    "ExtractionConfig",
    "extract_region",
    "iter_candidates_from_tsv",
    "JointMoleculeRecord",
    "FIELDS",
    "SCHEMA_VERSION",
    "EVALUATION_ONLY_FIELDS",
    "ExclusionReason",
    "JointEvidenceStore",
    "input_manifest_id",
    "describe_inputs",
]
