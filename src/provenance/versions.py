"""Capture what produced a result: tool versions, seeds, environment.

Every joint-molecule record carries a ``tool_versions`` string and an ``input_manifest_id``.
This module produces both halves of that provenance, and the run manifest that expands them.

The design goal is that a result table alone is enough to reconstruct which code and which
inputs made it, without consulting a lab notebook.
"""
from __future__ import annotations

import os
import platform
import random
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional

#: External binaries whose versions are recorded when present on PATH.
EXTERNAL_TOOLS = ("samtools", "bcftools", "tabix", "longphase", "whatshap", "modkit")

#: Python packages whose versions matter to the numbers produced.
PYTHON_PACKAGES = ("pysam", "numpy", "matplotlib", "scipy", "sklearn", "pyarrow")


def collect_tool_versions() -> Dict[str, str]:
    """Best-effort version capture. A missing tool is recorded as absent, never omitted.

    Recording absence matters: ``longphase`` being unavailable is exactly the kind of fact
    that explains a downstream result, and a manifest that silently omits it hides that.
    """
    versions: Dict[str, str] = {
        "python": platform.python_version(),
        "platform": platform.platform(),
    }

    for tool in EXTERNAL_TOOLS:
        versions[tool] = _external_version(tool)

    for package in PYTHON_PACKAGES:
        versions[package] = _package_version(package)

    return versions


def _external_version(tool: str) -> str:
    path = shutil.which(tool)
    if path is None:
        return "absent"
    try:
        completed = subprocess.run(
            [tool, "--version"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return "present:version_unavailable"
    output = (completed.stdout or completed.stderr or "").strip()
    return output.splitlines()[0].strip() if output else "present:version_unavailable"


def _package_version(package: str) -> str:
    try:
        module = __import__(package)
    except ImportError:
        return "absent"
    return str(getattr(module, "__version__", "present:version_unavailable"))


def format_tool_versions(versions: Optional[Dict[str, str]] = None, keys: Optional[List[str]] = None) -> str:
    """Render versions into the compact ``a=1;b=2`` form stored on every record.

    ``keys`` narrows the set, because the per-row string should stay short — the full
    dictionary lives once in the run manifest, not once per molecule.
    """
    versions = versions if versions is not None else collect_tool_versions()
    selected = keys or ["python", "pysam", "samtools"]
    return ";".join(f"{k}={versions.get(k, 'absent')}" for k in selected)


def resolve_seed(seed: Optional[int]) -> int:
    """Set every RNG this project uses and return the seed actually applied.

    A ``None`` seed is resolved to a drawn value which is then **recorded**, rather than
    left implicit — an unrecorded seed makes a stochastic result unreproducible even when
    everything else is captured.
    """
    if seed is None:
        seed = int.from_bytes(os.urandom(4), "little")
    random.seed(seed)
    try:
        import numpy as np

        np.random.seed(seed)
    except ImportError:
        pass
    return seed


def run_manifest(
    *,
    experiment_id: str,
    inputs: Dict,
    config: Dict,
    seed: Optional[int] = None,
    extra: Optional[Dict] = None,
) -> Dict:
    """Assemble the manifest written beside every output tree."""
    manifest = {
        "experiment_id": experiment_id,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "command": " ".join(sys.argv),
        "working_directory": os.getcwd(),
        "inputs": inputs,
        "config": config,
        "tool_versions": collect_tool_versions(),
        "seed": seed,
    }
    if extra:
        manifest.update(extra)
    return manifest
