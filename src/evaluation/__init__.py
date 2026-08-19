"""Feasibility counting, leakage-safe splitting, and metrics.

Metrics are returned as whole blocks with denominators attached, never as a bare number,
so a comparison cannot be reduced to a single figure of merit.
"""
from .funnel import (
    STAGES,
    FunnelCounts,
    count_funnel,
    format_funnel_tsv,
    profile_methylation,
    stratified_funnel,
)
from .metrics import MetricBlock, bootstrap_by_group, evaluate
from .splits import (
    CHROMOSOME,
    REGION,
    SAMPLE,
    Split,
    assert_disjoint,
    assert_no_region_crosses_split,
    make_split,
    selection_provenance,
)

__all__ = [
    "STAGES",
    "FunnelCounts",
    "count_funnel",
    "stratified_funnel",
    "profile_methylation",
    "format_funnel_tsv",
    "Split",
    "make_split",
    "assert_disjoint",
    "assert_no_region_crosses_split",
    "selection_provenance",
    "CHROMOSOME",
    "REGION",
    "SAMPLE",
    "MetricBlock",
    "evaluate",
    "bootstrap_by_group",
]
