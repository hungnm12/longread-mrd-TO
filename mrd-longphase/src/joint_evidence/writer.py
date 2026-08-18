"""Deterministic, resumable partition writer for joint-molecule records.

One gzip TSV per region, plus a sidecar run manifest. See the format trade-off in
``docs/joint_molecule_schema.md``.

Resumability contract
---------------------
A partition counts as complete only when a marker file exists under ``_complete/``. The
marker is written **after** the data file is closed and ``fsync``-ed, so an interrupted run
can never leave a marker pointing at a truncated partition. Incomplete partitions are
rewritten from scratch on the next run — never appended to, because appending to a
half-written gzip member would corrupt it silently.

Determinism contract
--------------------
Records are written in ``sort_key`` order with floats fixed to 3 dp, and gzip is given
``mtime=0`` so the compressed bytes do not encode the run time. Re-running a region
byte-reproduces its partition, which is what makes the fixtures diffable and the funnel's
counts checkable.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import logging
import os
from typing import Dict, Iterable, List, Optional

from .record import FIELDS, SCHEMA_VERSION, JointMoleculeRecord

LOGGER = logging.getLogger(__name__)

REGIONS_DIRNAME = "regions"
COMPLETE_DIRNAME = "_complete"
MANIFEST_FILENAME = "manifest.json"


class JointEvidenceStore:
    """Filesystem layout for one sample's joint-molecule evidence."""

    def __init__(self, root: str):
        self.root = root
        self.regions_dir = os.path.join(root, REGIONS_DIRNAME)
        self.complete_dir = os.path.join(root, COMPLETE_DIRNAME)

    def ensure_dirs(self) -> None:
        os.makedirs(self.regions_dir, exist_ok=True)
        os.makedirs(self.complete_dir, exist_ok=True)

    def partition_path(self, region_id: str) -> str:
        return os.path.join(self.regions_dir, f"{region_id}.tsv.gz")

    def marker_path(self, region_id: str) -> str:
        return os.path.join(self.complete_dir, region_id)

    def is_complete(self, region_id: str) -> bool:
        """A region is complete only if both its marker and its data file exist."""
        return os.path.exists(self.marker_path(region_id)) and os.path.exists(
            self.partition_path(region_id)
        )

    def completed_regions(self) -> List[str]:
        if not os.path.isdir(self.complete_dir):
            return []
        return sorted(
            name for name in os.listdir(self.complete_dir) if self.is_complete(name)
        )

    def write_partition(self, region_id: str, records: Iterable[JointMoleculeRecord]) -> int:
        """Write one region's records and mark it complete. Returns the row count.

        Writes to a ``.tmp`` file and renames, so a crash mid-write cannot leave a
        partially-written partition at the real path.
        """
        self.ensure_dirs()
        final_path = self.partition_path(region_id)
        tmp_path = final_path + ".tmp"

        rows = sorted(records, key=lambda r: r.sort_key)
        with gzip.GzipFile(tmp_path, "wb", mtime=0) as raw:
            raw.write(("\t".join(FIELDS) + "\n").encode())
            for record in rows:
                raw.write(("\t".join(record.to_row()) + "\n").encode())

        _fsync_path(tmp_path)
        os.replace(tmp_path, final_path)
        _fsync_dir(self.regions_dir)

        with open(self.marker_path(region_id), "w") as marker:
            marker.write(f"{len(rows)}\n")
        _fsync_dir(self.complete_dir)

        LOGGER.info("wrote partition %s (%d records)", region_id, len(rows))
        return len(rows)

    def read_partition(self, region_id: str) -> List[Dict[str, str]]:
        """Read a partition back as raw string cells. Parsing is the caller's business."""
        path = self.partition_path(region_id)
        with gzip.open(path, "rt") as fh:
            header = fh.readline().rstrip("\n").split("\t")
            return [
                dict(zip(header, line.rstrip("\n").split("\t")))
                for line in fh
                if line.strip()
            ]

    def write_manifest(self, manifest: Dict) -> str:
        """Write the run manifest. Sorted keys so it diffs cleanly between runs."""
        self.ensure_dirs()
        path = os.path.join(self.root, MANIFEST_FILENAME)
        with open(path, "w") as fh:
            json.dump(manifest, fh, indent=2, sort_keys=True)
            fh.write("\n")
        return path


def input_manifest_id(inputs: Dict[str, str], config: Optional[Dict] = None) -> str:
    """Content-addressed id joining every record to the exact input set that produced it.

    Hashes the *resolved* input paths and the extraction config, not file contents — the
    BAMs are 80 GB and read-only, so hashing them on every run is neither affordable nor
    informative. The trade-off: a silently modified input would not change this id. That is
    acceptable here because every input lives under a read-only path owned by another user
    (``docs/DATA_GOVERNANCE.md``), and file size and mtime are captured in the manifest
    alongside it.
    """
    payload = {
        "inputs": {k: inputs[k] for k in sorted(inputs)},
        "config": config or {},
        "schema_version": SCHEMA_VERSION,
    }
    digest = hashlib.sha1(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    )
    return digest.hexdigest()[:16]


def describe_inputs(paths: Dict[str, str]) -> Dict[str, Dict[str, object]]:
    """Record size and mtime for each input, for the manifest's provenance block."""
    described: Dict[str, Dict[str, object]] = {}
    for name, path in sorted(paths.items()):
        entry: Dict[str, object] = {"path": path, "exists": os.path.exists(path)}
        if entry["exists"]:
            stat = os.stat(path)
            entry["size_bytes"] = stat.st_size
            entry["mtime"] = int(stat.st_mtime)
        described[name] = entry
    return described


def _fsync_path(path: str) -> None:
    with open(path, "rb") as fh:
        os.fsync(fh.fileno())


def _fsync_dir(path: str) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
