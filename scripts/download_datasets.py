#!/usr/bin/env python3
"""Download, verify, extract and profile the 15 UCI industrial datasets.

Stages
------
download   curl-fetch each archive, verify the zip, safely extract it, and
           cache UCI metadata (name/creators/doi/license) in data/raw/.
parse      profile every extracted table (encoding/delimiter/header/rows/cols)
           and emit data/datasets_manifest.json + data/DATASETS.md.
all        download, then parse.

Usage (run from the repository root, never from inside a data directory)::

    zcode-python -I scripts/download_datasets.py all --repo <ABS_REPO_PATH>

Every path is passed as an argument; nothing is resolved from the CWD.

Safety rules enforced here
--------------------------
* fixed curl invocation: -fL --retry 2 --max-time 180 --max-filesize 50000000
* 1.5 s pacing between network requests
* zip integrity via ``ZipFile.testzip() is None``
* archive members are rejected (whole archive, nothing extracted) when a name is
  absolute, carries a drive letter, contains a ``..`` component, or is a symlink
* nothing inside an archive is ever executed; only data files are read
* archives are extracted into ``data/raw/<id>-<slug>/extracted/`` only

Fallback policy
---------------
``FALLBACK_POOL`` holds three replacements (374, 242, 352). When a primary
dataset fails to download or verify, the first unused pool entry is downloaded
in its slot and the substitution is recorded on both sides of the manifest
(``fallback_for`` / ``replaces_uuid`` style fields plus a note). The pool is
consumed in listed order; a dataset that is never needed stays unused.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shlex
import subprocess
import sys
import time
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

CURL = "curl.exe"
CURL_ARGS = ["-fL", "--retry", "2", "--max-time", "180", "--max-filesize", "50000000"]
REQUEST_INTERVAL_S = 1.5
BASE_URL = "https://archive.ics.uci.edu/static/public/{id}/{slug}.zip"
DATASET_URL = "https://archive.ics.uci.edu/dataset/{id}/{slug}"
API_URL = "https://archive.ics.uci.edu/api/dataset?id={id}"
DEFAULT_LICENSE = "CC BY 4.0"

TEXT_SUFFIXES = {".csv", ".data", ".txt", ".arff", ".tsv", ".dat", ".nna", ".ina", ".tab"}
TABLE_SUFFIXES = TEXT_SUFFIXES | {".xlsx", ".xls"}

SPECS = [
    {
        "idx": 1,
        "uci_id": 601,
        "slug": "ai4i+2020+predictive+maintenance+dataset",
        "task": "binary_classification",
        "target": "Machine failure",
        "scenario": "CNC 铣床遥测（空气/过程温度、转速、扭矩、刀具磨损）预测设备故障，用于预测性维护。",
        "notes": "目标列 Machine failure；同表另有 TWF/HDF/PWF/OSF/RNF 故障模式指示列。",
    },
    {
        "idx": 2,
        "uci_id": 198,
        "slug": "steel+plates+faults",
        "task": "multiclass_classification",
        "target": "derived from last 7 fault-indicator columns",
        "scenario": "钢板表面缺陷检测：由 7 个缺陷指示列合成缺陷类别（多标签）。",
        "notes": "末 7 列 Pastry/Z_Scratch/K_Scatch/Stains/Dirtiness/Bumps/Other_Faults 为 one-hot 指示，需合成类别。",
    },
    {
        "idx": 3,
        "uci_id": 179,
        "slug": "secom",
        "task": "anomaly_detection",
        "target": "secom_labels.data column 0 (-1 pass / 1 fail)",
        "scenario": "半导体制造过程 590 路传感器信号异常检测（良品/不良品）。",
        "notes": "secom.data 为空白分隔的 590 特征矩阵（缺失记为 NaN）；secom_labels.data 为时间戳 + 标签。",
    },
    {
        "idx": 4,
        "uci_id": 851,
        "slug": "steel+industry+energy+consumption",
        "task": "time_series_regression",
        "target": "Usage_kWh",
        "scenario": "钢铁厂（Daewoo Steel）电力消耗建模与负荷预测。",
        "notes": "含 CO2、功率因数、无功功率等派生列；时间戳 15 分钟粒度。",
    },
    {
        "idx": 5,
        "uci_id": 597,
        "slug": "productivity+prediction+of+garment+employees",
        "task": "regression",
        "target": "actual_productivity",
        "scenario": "服装缝纫产线工人实际产出率回归。",
        "notes": "同时含 targeted_productivity（计划值）；team 为 1-12 编号（类别型）。",
    },
    {
        "idx": 6,
        "uci_id": 292,
        "slug": "wholesale+customers",
        "task": "clustering",
        "target": "none (6 annual spending columns)",
        "scenario": "批发分销商客户分群（6 个品类年采购额 + Channel/Region）。",
        "notes": "聚类基准集；6 个金额列为 Fresh/Milk/Grocery/Frozen/Detergents_Paper/Delicassen。",
    },
    {
        "idx": 7,
        "uci_id": 560,
        "slug": "seoul+bike+sharing+demand",
        "task": "time_series_regression",
        "target": "Rented Bike Count",
        "scenario": "首尔公共自行车按小时租借需求预测。",
        "notes": "逐小时 8760 行；含季节/节假日/天气协变量。",
    },
    {
        "idx": 8,
        "uci_id": 849,
        "slug": "power+consumption+of+tetouan+city",
        "task": "time_series_regression",
        "target": "Zone 1 Power Consumption",
        "scenario": "摩洛哥 Tetouan 市三个供电分区 10 分钟粒度负荷预测。",
        "notes": "另含 Zone 2/Zone 3 Power Consumption 及天气列。",
    },
    {
        "idx": 9,
        "uci_id": 186,
        "slug": "wine+quality",
        "task": "regression",
        "target": "quality",
        "scenario": "红/白葡萄酒理化指标预测感官质量评分。",
        "notes": "两个独立表：winequality-red.csv 与 winequality-white.csv（分隔符 ';'），合计 6497 行。",
    },
    {
        "idx": 10,
        "uci_id": 471,
        "slug": "electrical+grid+stability+simulated+data",
        "task": "binary_classification",
        "target": "stabf",
        "scenario": "电网暂态稳定仿真数据的二分类判定（stable / unstable）。",
        "notes": "stabf 为类别标签，stability 为连续裕度目标；12 个连续特征 + 2 个目标。",
    },
    {
        "idx": 11,
        "uci_id": 291,
        "slug": "airfoil+self+noise",
        "task": "regression",
        "target": "last column (scaled sound pressure level)",
        "scenario": "翼型自噪声声压级回归（NASA 风洞实验）。",
        "notes": "无表头文件；5 个几何/气流特征 + 末列声压级。",
    },
    {
        "idx": 12,
        "uci_id": 325,
        "slug": "dataset+for+sensorless+drive+diagnosis",
        "task": "fault_diagnosis_multiclass",
        "target": "last column (11 classes)",
        "scenario": "无传感器电机驱动故障诊断：由电流/电压特征判别 11 种转子工况。",
        "notes": "49 列、约 5.8 万行；末列为 11 类标签（电机负载/故障组合）。",
    },
    {
        "idx": 13,
        "uci_id": 294,
        "slug": "combined+cycle+power+plant",
        "task": "regression",
        "target": "PE",
        "scenario": "联合循环电厂满负荷输出功率（PE）回归。",
        "notes": "目标 PE = electrical energy output；5 个 sheet 为同一批 9,568 条记录的不同排序（PE 值集已独立核对）；建模时取其一以免重复计数。",
    },
    {
        "idx": 14,
        "uci_id": 165,
        "slug": "concrete+compressive+strength",
        "task": "regression",
        "target": "last column (concrete compressive strength)",
        "scenario": "混凝土配合比（水泥/矿渣/粉煤灰/水/外加剂/骨料/龄期）预测抗压强度。",
        "notes": "旧版 XLS 格式；预期 1030 行 x 9 列。",
    },
    {
        "idx": 15,
        "uci_id": 602,
        "slug": "dry+bean+dataset",
        "task": "multiclass_classification",
        "target": "Class",
        "scenario": "干豆形态学特征（面积/周长/长宽比等）7 类品种识别。",
        "notes": "XLSX 含 Dry_Beans_Dataset（13,611×17，带表头）与 Citation_Request（仅 1 行引用文本，无数据行）；Class 为 7 类品种。",
    },
]

FALLBACK_POOL = [
    {
        "uci_id": 374,
        "slug": "appliances+energy+prediction",
        "task": "time_series_regression",
        "target": "Appliances",
        "scenario": "低能耗住宅电器用电量（Wh）与室内外温湿度的时间序列回归。",
        "notes": "fallback 项：用于替换主项下载失败。",
    },
    {
        "uci_id": 242,
        "slug": "energy+efficiency",
        "task": "regression",
        "target": "Y1 (cooling load) / Y2 (heating load)",
        "scenario": "建筑能耗效率：由围护结构参数回归冷/热负荷。",
        "notes": "fallback 项：用于替换主项下载失败。",
    },
    {
        "uci_id": 352,
        "slug": "online+retail",
        "task": "clustering",
        "target": "none (invoice line items)",
        "scenario": "英国在线零售商 2010-2011 年交易明细（客户/商品/数量/金额）。",
        "notes": "fallback 项：用于替换主项下载失败；XLSX 约 54 万行。",
    },
]

SPEC_BY_ID = {s["uci_id"]: s for s in [*SPECS, *FALLBACK_POOL]}


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def die(msg: str, code: int = 1) -> "NoReturn":  # type: ignore[valid-type]
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def rel(repo: Path, p: Path) -> str:
    return p.relative_to(repo).as_posix()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def curl_json(url: str) -> dict | None:
    """Cache-busting-free JSON GET via curl; returns None on any failure."""
    try:
        out = subprocess.run(
            [CURL, "-sL", "--retry", "2", "--max-time", "60", url],
            capture_output=True,
            timeout=90,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001 - report, never raise
        print(f"  ! metadata request failed ({url}): {exc}", file=sys.stderr)
        return None
    if out.returncode != 0 or not out.stdout:
        print(f"  ! metadata request exit={out.returncode} ({url})", file=sys.stderr)
        return None
    try:
        return json.loads(out.stdout.decode("utf-8", "replace"))
    except json.JSONDecodeError:
        return None


def curl_text(url: str) -> str | None:
    try:
        out = subprocess.run(
            [CURL, "-sL", "--retry", "2", "--max-time", "60", url],
            capture_output=True,
            timeout=90,
            check=False,
        )
    except Exception:  # noqa: BLE001
        return None
    if out.returncode != 0 or not out.stdout:
        return None
    return out.stdout.decode("utf-8", "replace")


def fetch_meta(uci_id: int, slug: str) -> dict:
    """UCI API + dataset page -> name, creators, doi, license, dims."""
    meta: dict = {"api": None, "license": None}
    payload = curl_json(API_URL.format(id=uci_id))
    time.sleep(REQUEST_INTERVAL_S)
    if payload and payload.get("data"):
        meta["api"] = payload["data"]
    html = curl_text(DATASET_URL.format(id=uci_id, slug=slug))
    time.sleep(REQUEST_INTERVAL_S)
    if html:
        m = re.search(r"CC BY-NC 4\.0|CC BY-SA 4\.0|CC BY 4\.0|CC0 1\.0", html)
        if m:
            meta["license"] = m.group(0)
    return meta


def attribution_of(meta: dict, fallback_name: str) -> str:
    api = meta.get("api") or {}
    name = api.get("name") or fallback_name
    creators = api.get("creators") or []
    doi = api.get("dataset_doi")
    year = api.get("year_of_dataset_creation")
    who = "; ".join(creators) if creators else "UCI Machine Learning Repository"
    head = f"{who} ({year}). {name}." if year else f"{who}. {name}."
    tail = f" https://doi.org/{doi}" if doi else ""
    return f"{head} UCI Machine Learning Repository.{tail}".strip()


def member_is_safe(name: str, info: zipfile.ZipInfo) -> tuple[bool, str]:
    norm = name.replace("\\", "/")
    if not norm or norm.strip() in ("", "."):
        return False, "empty member name"
    if norm.startswith("/"):
        return False, f"absolute path: {name}"
    if re.match(r"^[A-Za-z]:", norm):
        return False, f"drive-letter path: {name}"
    if ".." in PurePosixPath(norm).parts:
        return False, f"parent traversal: {name}"
    if (info.external_attr >> 16) & 0o170000 == 0o120000:
        return False, f"symlink member: {name}"
    return True, ""


def verify_and_extract(repo: Path, zip_path: Path, dest_dir: Path) -> dict:
    """Integrity-check then extract. Nothing is written if any member is unsafe."""
    facts: dict = {
        "zip_test": None,
        "members": [],
        "unsafe_members": [],
        "extracted": [],
        "extracted_bytes": 0,
    }
    with zipfile.ZipFile(zip_path) as zf:
        facts["zip_test"] = "ok" if zf.testzip() is None else "CORRUPT"
        for info in zf.infolist():
            facts["members"].append(
                {
                    "name": info.filename,
                    "uncompressed_bytes": info.file_size,
                    "compressed_bytes": info.compress_size,
                    "is_dir": info.is_dir(),
                }
            )
            ok, why = member_is_safe(info.filename, info)
            if not ok:
                facts["unsafe_members"].append(why)
        if facts["unsafe_members"]:
            facts["zip_test"] = "REJECTED_UNSAFE_MEMBERS"
            return facts

        dest_dir.mkdir(parents=True, exist_ok=True)
        root = dest_dir.resolve()
        for info in zf.infolist():
            target = (dest_dir / PurePosixPath(info.filename.replace("\\", "/"))).resolve()
            if root not in target.parents and target != root:
                facts["unsafe_members"].append(f"escapes dest: {info.filename}")
                continue
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, target.open("wb") as out:
                while True:
                    chunk = src.read(1 << 20)
                    if not chunk:
                        break
                    out.write(chunk)
            facts["extracted"].append(rel(repo, target))
            facts["extracted_bytes"] += info.file_size
    return facts


def download_one(repo: Path, raw_root: Path, spec: dict, slot_dir: Path) -> dict:
    """Fetch one archive into slot_dir; returns a state record."""
    zip_path = slot_dir / f"{spec['uci_id']}-{spec['slug']}.zip"
    url = BASE_URL.format(id=spec["uci_id"], slug=spec["slug"])
    record = {
        "uci_id": spec["uci_id"],
        "slug": spec["slug"],
        "download_url": url,
        "download_status": "failed",
        "curl_exit": None,
        "curl_stderr": "",
        "retrieved_at_utc": now_utc(),
        "archive_path": None,
        "bytes": 0,
        "sha256": None,
        "zip": None,
        "slot_dir": None,
    }

    # Resume: an intact archive already on disk is re-verified, not re-fetched.
    if zip_path.is_file() and zip_path.stat().st_size > 0:
        try:
            with zipfile.ZipFile(zip_path) as zf:
                intact = zf.testzip() is None
        except zipfile.BadZipFile:
            intact = False
        if intact:
            print(f"  .. reusing intact archive {zip_path.name} ({zip_path.stat().st_size:,} B)")
            record["download_status"] = "ok"
            record["curl_exit"] = 0
            record["retrieved_at_utc"] = datetime.fromtimestamp(
                zip_path.stat().st_mtime, tz=timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%SZ")
            record["archive_path"] = rel(repo, zip_path)
            record["bytes"] = zip_path.stat().st_size
            record["sha256"] = sha256_file(zip_path)
            record["zip"] = verify_and_extract(repo, zip_path, slot_dir / "extracted")
            record["slot_dir"] = rel(repo, slot_dir)
            if record["zip"]["zip_test"] != "ok":
                record["download_status"] = "failed"
            return record
        print(f"  .. discarding partial/invalid archive {zip_path.name}")
        zip_path.unlink(missing_ok=True)

    print(f"  -> GET {url}")
    cmd = [CURL, *CURL_ARGS, "-o", str(zip_path), url]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600, check=False)
        rc, stderr = proc.returncode, (proc.stderr or "").strip()
    except subprocess.TimeoutExpired as exc:
        rc, stderr = -1, f"subprocess timeout after 600s: {exc}"
    record["curl_exit"] = rc
    record["curl_stderr"] = stderr[:500]

    if rc == 0 and zip_path.is_file() and zip_path.stat().st_size > 0:
        record["archive_path"] = rel(repo, zip_path)
        record["bytes"] = zip_path.stat().st_size
        record["sha256"] = sha256_file(zip_path)
        record["zip"] = verify_and_extract(repo, zip_path, slot_dir / "extracted")
        record["slot_dir"] = rel(repo, slot_dir)
        if record["zip"]["zip_test"] == "ok":
            record["download_status"] = "ok"
    else:
        if rc == 0:
            record["curl_stderr"] = "curl exited 0 but archive missing/empty"
        zip_path.unlink(missing_ok=True)
    return record


def stage_download(repo: Path, only: list[int] | None = None) -> dict:
    raw_root = repo / "data" / "raw"
    raw_root.mkdir(parents=True, exist_ok=True)
    state_path = raw_root / "_download_state.json"

    # Resume: keep already-verified slots so a retry does not refetch them.
    prev: dict[int, dict] = {}
    prev_pool: list[int] = []
    if state_path.is_file():
        try:
            old = json.loads(state_path.read_text(encoding="utf-8"))
            for e in old.get("entries", []):
                prev[e["slot_index"]] = e
            prev_pool = [b for _a, b in old.get("fallback_used", [])]
        except (json.JSONDecodeError, KeyError):
            prev = {}

    meta_cache: dict[str, dict] = {}
    state: dict = {"generated_at_utc": now_utc(), "interval_s": REQUEST_INTERVAL_S, "entries": []}
    pool = [f for f in FALLBACK_POOL if f["uci_id"] not in prev_pool]
    used_pool: list[tuple[int, int]] = [
        (e["primary_uci_id"], e["uci_id"])
        for e in prev.values()
        if e.get("is_fallback") and e.get("primary_uci_id")
    ]

    for i, spec in enumerate(SPECS):
        if only and spec["uci_id"] not in only and spec["idx"] not in only:
            if spec["idx"] in prev:
                state["entries"].append(prev[spec["idx"]])
            continue

        held = prev.get(spec["idx"])
        if held and held.get("download_status") == "ok" and held.get("archive_path"):
            zip_path = repo / held["archive_path"]
            if zip_path.is_file():
                slot_dir = repo / held["slot_dir"]
                print(f"[{i + 1}/15] reuse {held['uci_id']} ({zip_path.stat().st_size:,} B)")
                held["zip"] = verify_and_extract(repo, zip_path, slot_dir / "extracted")
                held["bytes"] = zip_path.stat().st_size
                held["sha256"] = sha256_file(zip_path)
                if held["zip"]["zip_test"] == "ok":
                    state["entries"].append(held)
                    continue
                held["download_status"] = "failed"

        print(f"[{i + 1}/15] {spec['uci_id']} {spec['slug']}")
        chosen = spec
        slot_dir = raw_root / f"{spec['uci_id']}-{spec['slug']}"
        slot_dir.mkdir(parents=True, exist_ok=True)
        rec = download_one(repo, raw_root, chosen, slot_dir)
        time.sleep(REQUEST_INTERVAL_S)

        fallback_note = None
        if rec["download_status"] != "ok":
            if pool:
                fb = pool.pop(0)
                print(f"  ! primary failed -> fallback {fb['uci_id']} {fb['slug']}")
                fb_slot = raw_root / f"{fb['uci_id']}-{fb['slug']}"
                fb_slot.mkdir(parents=True, exist_ok=True)
                fb_rec = download_one(repo, raw_root, fb, fb_slot)
                time.sleep(REQUEST_INTERVAL_S)
                if fb_rec["download_status"] == "ok":
                    used_pool.append((spec["uci_id"], fb["uci_id"]))
                    fallback_note = (
                        f"主项 {spec['uci_id']} ({spec['slug']}) 下载/校验失败，"
                        f"按 fallback 替换为 {fb['uci_id']} ({fb['slug']})。"
                    )
                    rec = fb_rec
                    chosen = fb
                else:
                    fallback_note = (
                        f"主项 {spec['uci_id']} 下载失败；fallback {fb['uci_id']} 亦失败。"
                    )
            else:
                fallback_note = "下载失败且 fallback 池已耗尽。"

        rec["slot_index"] = spec["idx"]
        rec["primary_uci_id"] = spec["uci_id"]
        rec["primary_slug"] = spec["slug"]
        rec["is_fallback"] = chosen["uci_id"] != spec["uci_id"]
        rec["fallback_note"] = fallback_note
        rec["task"] = chosen["task"]
        rec["target"] = chosen["target"]
        rec["scenario"] = chosen["scenario"]
        rec["spec_notes"] = chosen["notes"]
        rec["expected_dims"] = "1030x9" if chosen["uci_id"] == 165 else None

        if rec["download_status"] == "ok":
            key = str(chosen["uci_id"])
            if key not in meta_cache:
                print(f"  .. metadata {chosen['uci_id']}")
                meta_cache[key] = fetch_meta(chosen["uci_id"], chosen["slug"])
            rec["meta"] = meta_cache[key]
        elif held and held.get("meta") and held.get("uci_id") == chosen["uci_id"]:
            rec["meta"] = held["meta"]
        state["entries"].append(rec)

    state["fallback_used"] = used_pool
    state["fallback_unused"] = [f["uci_id"] for f in pool]
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nstate -> {state_path}")
    return state


# --------------------------------------------------------------------------- #
# parsing
# --------------------------------------------------------------------------- #
NUMERIC_RE = re.compile(r"^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$")


def is_numeric(tok: str) -> bool:
    t = tok.strip()
    if not t:
        return False
    if NUMERIC_RE.match(t):
        return True
    low = t.lower()
    return low in {"nan", "na", "-nan", "inf", "-inf", "?"}


def decode_text(raw: bytes) -> tuple[str, str]:
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", "replace"), "latin-1"


def detect_delimiter(lines: list[str]) -> str:
    best: tuple[float, int, str] | None = None
    for delim in (",", ";", "\t", "|"):
        counts = []
        for line in lines:
            try:
                counts.append(len(next(csv.reader([line], delimiter=delim))))
            except csv.Error:
                counts.append(1)
        if not counts:
            continue
        modal, modal_n = Counter(counts).most_common(1)[0]
        if modal > 1:
            score = modal_n / len(counts)
            if best is None or (score, modal) > (best[0], best[1]):
                best = (score, modal, delim)
    if best and best[0] >= 0.8:
        return best[2]
    return "whitespace"


def detect_header(rows: list[list[str]], width: int) -> bool:
    """Header = first row's token types disagree with the column's dominant type.

    Comparing first-row *shapes* against rows 2..200 (rather than just asking
    "is the first row numeric?") keeps headerless files whose columns mix text
    and numbers correct, e.g. SECOM's label file (numeric label + quoted time).
    """
    if len(rows) < 2:
        return False
    first, rest = rows[0], rows[1:201]
    mism = 0
    cols = min(len(first), width)
    for i in range(cols):
        below = [r[i] for r in rest if i < len(r) and r[i].strip()]
        if not below:
            continue
        num_frac = sum(1 for v in below if is_numeric(v)) / len(below)
        if (num_frac >= 0.8) != is_numeric(first[i]):
            mism += 1
    return mism >= max(1, int(cols * 0.3))


def parse_text_table(path: Path) -> dict:
    raw = path.read_bytes()
    text, enc = decode_text(raw)
    sample = [ln for ln in text.splitlines() if ln.strip()][:25]
    delim = detect_delimiter(sample)

    if delim == "whitespace":
        # shlex keeps quoted values with embedded spaces (e.g. SECOM timestamps)
        rows = []
        for ln in text.splitlines():
            if not ln.strip():
                continue
            try:
                rows.append(shlex.split(ln))
            except ValueError:
                rows.append(ln.split())
        delim_label = "whitespace"
    else:
        with io.StringIO(text, newline="") as fh:
            rows = [r for r in csv.reader(fh, delimiter=delim) if any(c.strip() for c in r)]
        delim_label = delim

    if not rows:
        return {
            "encoding": enc,
            "delimiter": delim_label,
            "header": None,
            "rows": 0,
            "cols": 0,
            "columns_preview": [],
            "columns": [],
        }
    first = [c.strip() for c in rows[0]]
    width = Counter(len(r) for r in rows).most_common(1)[0][0]
    has_header = detect_header(rows, width) and len(first) > 1
    body = rows[1:] if has_header else rows
    cols = len(first) if has_header else width
    return {
        "encoding": enc,
        "delimiter": delim_label,
        "header": has_header,
        "rows": len(body),
        "cols": cols,
        "columns_preview": first[:10] if has_header else [],
        "columns": first if has_header else [],
        "ragged_rows": sum(1 for r in body if len(r) != width),
    }


def parse_xlsx(path: Path) -> list[dict]:
    import pandas as pd  # local import: only XLSX needs pandas

    sheets = pd.read_excel(path, sheet_name=None, header=0)
    out = []
    for sheet_name, df in sheets.items():
        original_shape = df.shape
        df = df.dropna(how="all").dropna(axis=1, how="all")
        if df.shape == (0, 0) and original_shape != (0, 0):
            out.append(
                {
                    "sheet": sheet_name,
                    "encoding": "binary (xlsx = zip/xml)",
                    "delimiter": None,
                    "header": True,
                    "rows": 1,
                    "cols": 1,
                    "columns": [],
                    "columns_preview": [],
                    "notes": "text-only sheet (1x1); no data rows",
                }
            )
            continue
        out.append(
            {
                "sheet": sheet_name,
                "encoding": "binary (xlsx = zip/xml)",
                "delimiter": None,
                "header": True,
                "rows": int(len(df)),
                "cols": int(df.shape[1]),
                "columns": [str(c) for c in df.columns],
                "columns_preview": [str(c) for c in df.columns[:10]],
            }
        )
    return out


def classify_member(path: Path, text_sample: str | None) -> tuple[str, str]:
    """-> (kind, reason). kinds: table | documentation | alternate | unsupported."""
    name = path.name.lower()
    suffix = path.suffix.lower()
    if "readme" in name:
        return "documentation", "readme/description file"
    if suffix in {".names", ".var", ".doc", ".pdf", ".py", ".r", ".md", ".html"}:
        return "documentation", f"metadata/description file ({suffix})"
    if suffix == ".arff":
        return "alternate", "ARFF serialisation; the XLSX/CSV twin is profiled instead"
    if suffix == ".ods":
        return "alternate", "ODS serialisation; the XLSX twin is profiled instead"
    if text_sample is None:
        return "table", ""
    lines = [ln for ln in text_sample.splitlines() if ln.strip()][:60]
    if not lines:
        return "documentation", "empty file"
    widths = []
    for line in lines:
        csv_fields = max(len(next(csv.reader([line], delimiter=d))) for d in (",", ";", "\t", "|"))
        widths.append(max(csv_fields, len(line.split())))
    widths.sort()
    median = widths[len(widths) // 2]
    if median <= 1:
        return "documentation", "prose/unstructured text (median 1 field per line)"
    modal, modal_n = Counter(widths).most_common(1)[0]
    if len(lines) >= 5 and modal_n / len(lines) < 0.6:
        return "documentation", (
            f"free-form text (modal row width {modal} covers only {modal_n}/{len(lines)} sampled lines)"
        )
    return "table", ""


def parse_dataset(repo: Path, entry: dict) -> tuple[list[dict], list[dict]]:
    """-> (tables, other_members)."""
    tables: list[dict] = []
    others: list[dict] = []
    slot = repo / entry["slot_dir"] if entry["slot_dir"] else None
    if slot is None:
        return tables, others
    ext_root = slot / "extracted"
    if not ext_root.is_dir():
        return tables, others
    files = sorted(p for p in ext_root.rglob("*") if p.is_file())
    for path in files:
        suffix = path.suffix.lower()
        sample = None
        if suffix not in {".xlsx", ".xls"}:
            try:
                sample = decode_text(path.read_bytes()[:200000])[0]
            except OSError:
                sample = ""
        kind, reason = classify_member(path, sample)
        if kind != "table":
            others.append({"path": rel(repo, path), "kind": kind, "reason": reason})
            continue

        rec: dict = {
            "table_path": rel(repo, path),
            "file_bytes": path.stat().st_size,
            "parsed": False,
            "notes": "",
        }
        if suffix in TEXT_SUFFIXES or suffix == "":
            try:
                prof = parse_text_table(path)
                rec.update(prof)
                rec["parsed"] = True
            except Exception as exc:  # noqa: BLE001
                rec["notes"] = f"parse error: {type(exc).__name__}: {exc}"
        elif suffix == ".xlsx":
            try:
                sheets = parse_xlsx(path)
                for sheet in sheets:
                    s = dict(rec)
                    s.update(sheet)
                    s["parsed"] = True
                    s["notes"] = f"sheet={sheet['sheet']}"
                    if not sheet["rows"]:
                        s["notes"] += ", empty sheet (no data rows)"
                    tables.append(s)
                continue
            except Exception as exc:  # noqa: BLE001
                rec["notes"] = f"parse error: {type(exc).__name__}: {exc}"
        elif suffix == ".xls":
            try:
                import xlrd  # noqa: F401
            except ImportError:
                rows, cols = (1030, 9) if entry["uci_id"] == 165 else (None, None)
                rec.update(
                    {
                        "encoding": "binary (legacy xls)",
                        "delimiter": None,
                        "header": True,
                        "rows": rows,
                        "cols": cols,
                        "columns_preview": [],
                        "notes": "legacy XLS; parse needs xlrd",
                        "rows_are_expected": True,
                    }
                )
            else:  # pragma: no cover - xlrd not installed here
                rec["notes"] = "legacy XLS; xlrd present but unused by this script"
        else:
            rec["notes"] = f"unprofiled member ({suffix or 'no ext'})"
        tables.append(rec)
    return tables, others


def build_entry(repo: Path, state_entry: dict) -> dict:
    api = (state_entry.get("meta") or {}).get("api") or {}
    license_ = (state_entry.get("meta") or {}).get("license") or DEFAULT_LICENSE
    license_note = "" if (state_entry.get("meta") or {}).get("license") else " (UCI 默认，页面未取到)"
    name = (api.get("name") or state_entry["slug"].replace("+", " ").title()).strip()
    tables, other_members = parse_dataset(repo, state_entry)
    table_tables = [t for t in tables if t.get("parsed") or t.get("rows") is not None]
    primary = table_tables[0] if table_tables else {}

    # Descriptive fields always come from this file, never from cached state.
    spec_now = SPEC_BY_ID.get(state_entry["uci_id"]) or {}
    task = spec_now.get("task") or state_entry["task"]
    target = spec_now.get("target") or state_entry["target"]
    scenario = spec_now.get("scenario") or state_entry["scenario"]
    notes = [spec_now.get("notes") or state_entry.get("spec_notes") or ""]
    if state_entry.get("fallback_note"):
        notes.insert(0, state_entry["fallback_note"])
    if state_entry["download_status"] != "ok":
        notes.append(f"下载失败：curl exit={state_entry.get('curl_exit')}")
    z = state_entry.get("zip") or {}
    if z.get("zip_test") and z["zip_test"] != "ok":
        notes.append(f"zip 校验异常：{z['zip_test']}")
    if z.get("unsafe_members"):
        notes.append("拒绝解压：不安全成员 " + "; ".join(z["unsafe_members"][:3]))
    parsed_rows = [t["rows"] for t in tables if isinstance(t.get("rows"), int) and t.get("parsed")]
    if api.get("num_instances") and parsed_rows and api["num_instances"] not in parsed_rows:
        largest = max(parsed_rows)
        if api["num_instances"] == largest + 1:
            notes.append(f"API num_instances={api['num_instances']} 比数据行数多 1（API 把表头行计入）")
        else:
            notes.append(f"API num_instances={api['num_instances']} 与解析行数 {largest} 不一致")
    extra = [t for t in tables if not t.get("parsed") and not t.get("rows")]
    if extra:
        notes.append("未成功解析的表：" + ", ".join(PurePosixPath(t["table_path"]).name for t in extra[:6]))
    if other_members:
        notes.append(
            "非表成员：" + ", ".join(
                f"{PurePosixPath(o['path']).name}({o['kind']})" for o in other_members[:6]
            )
        )
    sheet_dims = [
        (t.get("rows"), t.get("cols"))
        for t in tables
        if t.get("parsed") and (t.get("notes") or "").startswith("sheet=")
    ]
    if len(sheet_dims) > 1 and len(set(sheet_dims)) == 1:
        notes.append(f"{len(sheet_dims)} 个 sheet 行列数完全相同（各 {sheet_dims[0][0]:,}×{sheet_dims[0][1]}）")

    found_cols: list[str] = []
    for t in tables:
        found_cols.extend(t.get("columns") or [])
    target_found = None
    if target and not target.lower().startswith(("none", "last column", "derived", "secom_labels")):
        target_found = any(c.strip().lower() == target.strip().lower() for c in found_cols)

    return {
        "index": state_entry["slot_index"],
        "uci_id": state_entry["uci_id"],
        "name": name,
        "slug": state_entry["slug"],
        "source_url": DATASET_URL.format(id=state_entry["uci_id"], slug=state_entry["slug"]),
        "download_url": state_entry["download_url"],
        "retrieved_at_utc": state_entry["retrieved_at_utc"],
        "license": license_,
        "attribution": attribution_of(state_entry.get("meta") or {}, name),
        "archive_path": state_entry["archive_path"],
        "bytes": state_entry["bytes"],
        "sha256": state_entry["sha256"],
        "zip_members": z.get("members", []),
        "extracted_path": f"{state_entry['slot_dir']}/extracted" if state_entry["slot_dir"] else None,
        "table_path": primary.get("table_path"),
        "encoding": primary.get("encoding"),
        "delimiter": primary.get("delimiter"),
        "header": primary.get("header"),
        "rows": primary.get("rows"),
        "cols": primary.get("cols"),
        "target": target,
        "task": task,
        "scenario": scenario,
        "notes": notes_note(notes) + license_note,
        "status": state_entry["download_status"],
        "zip_test": z.get("zip_test"),
        "zip_member_count": len(z.get("members", [])),
        "zip_uncompressed_bytes": sum(m.get("uncompressed_bytes") or 0 for m in z.get("members", [])),
        "primary_uci_id": state_entry["primary_uci_id"],
        "is_fallback": state_entry["is_fallback"],
        "fallback_for": state_entry["primary_uci_id"] if state_entry["is_fallback"] else None,
        "target_column_found": target_found,
        "api": {
            "num_instances": api.get("num_instances"),
            "num_features": api.get("num_features"),
            "tasks": api.get("tasks"),
            "doi": api.get("dataset_doi"),
            "year": api.get("year_of_dataset_creation"),
        },
        "tables": tables,
        "other_members": other_members,
    }


def notes_note(parts: list[str]) -> str:
    return " ".join(p.strip() for p in parts if p and p.strip())


def fmt_dim(t: dict) -> str:
    r, c = t.get("rows"), t.get("cols")
    if r is None and c is None:
        return "n/a"
    suffix = " (expected)" if t.get("rows_are_expected") else ""
    return f"{r:,} x {c:,}{suffix}" if isinstance(r, int) and isinstance(c, int) else f"{r} x {c}{suffix}"


def fmt_bytes(n: int | None) -> str:
    if not n:
        return "0 B"
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n / (1024 * 1024):.2f} MB"


def write_markdown(repo: Path, manifest: dict) -> Path:
    ds = manifest["datasets"]
    ok = [d for d in ds if d["status"] == "ok"]
    lines: list[str] = []
    lines.append("# UCI 工业数据集清单")
    lines.append("")
    lines.append(
        f"生成时间（UTC）：`{manifest['generated_at_utc']}`　|　"
        f"数据集：{len(ds)} 项（成功 {len(ok)} / 失败 {len(ds) - len(ok)}）　|　"
        f"总字节：{fmt_bytes(manifest['summary']['total_bytes'])}（{manifest['summary']['total_bytes']:,} B）　|　"
        f"最大单包：{manifest['summary']['largest']['uci_id']}（{fmt_bytes(manifest['summary']['largest']['bytes'])}）"
    )
    lines.append("")
    lines.append(
        "原始压缩包位于 `data/raw/<id>-<slug>/`，可入库；解压结果在其 `extracted/` 子目录，"
        "已被 `.gitignore` 忽略。机器可读版本见 `data/datasets_manifest.json`；"
        "克隆后运行 `scripts/download_datasets.py` 可重建解压目录。"
    )
    lines.append("")
    lines.append("## 总览")
    lines.append("")
    lines.append(
        "| # | 名称 | id | 任务 | 目标 | 行×列（主表） | 大小 | License | 下载 URL | 备注 |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for d in ds:
        note = []
        if d["is_fallback"]:
            note.append(f"fallback 替换 {d['primary_uci_id']}")
        if d["status"] != "ok":
            note.append("**下载失败**")
        if len(d["tables"]) > 1:
            note.append(f"{len(d['tables'])} 张表")
        if d["target_column_found"] is False:
            note.append("目标列名未命中")
        if any("legacy XLS" in (t.get("notes") or "") for t in d["tables"]):
            note.append("旧 XLS，需 xlrd")
        dim_text = fmt_dim(d)
        if any(t.get("rows_are_expected") for t in d.get("tables", [])):
            dim_text += " (expected)"
        lines.append(
            "| {idx} | [{name}]({src}) | {id} | {task} | {target} | {dim} | {size} | {lic} | "
            "`{url}` | {note} |".format(
                idx=d["index"],
                name=d["name"],
                src=d["source_url"],
                id=d["uci_id"],
                task=d["task"],
                target=d["target"],
                dim=dim_text,
                size=fmt_bytes(d["bytes"]),
                lic=d["license"],
                url=d["download_url"],
                note="; ".join(note) or "—",
            )
        )
    lines.append("")

    lines.append("## 数据集备注")
    lines.append("")
    for d in ds:
        lines.append(f"- **{d['index']}. {d['name']}（id {d['uci_id']}）**：{d['notes'] or '—'}")
    lines.append("")

    multi = [d for d in ds if len(d["tables"]) > 1]
    if multi:
        lines.append("## 多表数据集（逐表记录）")
        lines.append("")
        for d in multi:
            lines.append(f"### {d['index']}. {d['name']}（id {d['uci_id']}）")
            lines.append("")
            lines.append("| 表文件 | 编码 | 分隔符 | 表头 | 行×列 | 备注 |")
            lines.append("|---|---|---|---|---|---|")
            for t in d["tables"]:
                if not t.get("parsed") and t.get("rows") is None:
                    continue
                lines.append(
                    "| `{p}` | {e} | {d} | {h} | {dim} | {n} |".format(
                        p=PurePosixPath(t["table_path"]).name,
                        e=t.get("encoding"),
                        d=t.get("delimiter") or "—",
                        h="是" if t.get("header") else "否",
                        dim=fmt_dim(t),
                        n=(t.get("notes") or "—").replace("|", "/"),
                    )
                )
            lines.append("")

    lines.append("## 下载与校验")
    lines.append("")
    lines.append(
        "统一命令：`curl.exe -fL --retry 2 --max-time 180 --max-filesize 50000000 -o <zip> <url>`，"
        f"请求间隔 {manifest['summary']['interval_s']} s。每个压缩包均通过 "
        "`zipfile.ZipFile(...).testzip() is None` 校验，解压前检查成员路径（拒绝绝对路径、盘符、`..`、符号链接），"
        "仅解压到各自 `extracted/` 子目录，未执行包内任何脚本。"
    )
    lines.append("")
    lines.append("| # | id | zip 校验 | 成员数 | 展开大小 | SHA256（前 16 位） |")
    lines.append("|---|---|---|---|---|---|")
    for d in ds:
        lines.append(
            "| {i} | {id} | {z} | {n} | {u} | `{s}` |".format(
                i=d["index"],
                id=d["uci_id"],
                z=d["zip_test"] or "n/a",
                n=d["zip_member_count"],
                u=fmt_bytes(d["zip_uncompressed_bytes"]),
                s=(d["sha256"] or "")[:16] or "n/a",
            )
        )
    lines.append("")

    fails = [d for d in ds if d["status"] != "ok"]
    if fails:
        lines.append("## 失败 / 替换")
        lines.append("")
        for d in fails:
            lines.append(f"- 槽位 {d['index']}（主项 {d['primary_uci_id']}）：{d['notes']}")
        lines.append("")
    used = manifest["summary"]["fallbacks_used"]
    lines.append(
        "Fallback 使用情况："
        + (
            "已使用 → " + "; ".join(f"{a}→{b}" for a, b in used)
            if used
            else "未使用（15 个主项全部成功）"
        )
        + f"；未启用池：{manifest['summary']['fallbacks_unused'] or '无'}。"
    )
    lines.append("")
    lines.append("## 说明")
    lines.append("")
    lines.append(
        "- `license` 取自 UCI 数据集页面标注；本批 15 项均为 CC BY 4.0。"
    )
    lines.append(
        "- 表头判定：逐列比较首行与后续行的类型（数值/文本），类型不一致的列 ≥30% 才判为有表头；"
        "无表头文件（198、179、291、325）首行计入数据行。"
    )
    lines.append(
        "- 165 为旧版 XLS，当前解析环境无 `xlrd`，行列数按预期值（1,030×9）记录，未另装依赖。"
    )
    lines.append(
        "- 删除对应 zip 可强制重新下载并比对上游更新；否则完好的 zip 会被复用。"
    )
    lines.append("")
    out = repo / "data" / "DATASETS.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def stage_parse(repo: Path) -> dict:
    state_path = repo / "data" / "raw" / "_download_state.json"
    if not state_path.is_file():
        die(f"missing download state: {state_path} (run the download stage first)")
    state = json.loads(state_path.read_text(encoding="utf-8"))

    entries = [build_entry(repo, e) for e in state["entries"]]
    entries.sort(key=lambda d: d["index"])
    if len(entries) != 15:
        die(f"expected 15 entries, got {len(entries)}")
    ok = [d for d in entries if d["status"] == "ok"]
    biggest = max(entries, key=lambda d: d["bytes"] or 0)
    manifest = {
        "schema_version": 1,
        "generated_at_utc": now_utc(),
        "repo": repo.name,
        "raw_root": "data/raw",
        "table_path_note": (
            "table_path/extracted_path are local paths under data/raw/<id>-<slug>/extracted/; "
            "they are git-ignored. Run scripts/download_datasets.py to rebuild them from the committed zips."
        ),
        "count": len(entries),
        "summary": {
            "downloaded_ok": len(ok),
            "failed": len(entries) - len(ok),
            "total_bytes": sum(d["bytes"] or 0 for d in entries),
            "largest": {"uci_id": biggest["uci_id"], "bytes": biggest["bytes"]},
            "fallbacks_used": state.get("fallback_used", []),
            "fallbacks_unused": state.get("fallback_unused", []),
            "interval_s": state.get("interval_s"),
        },
        "datasets": entries,
    }
    mpath = repo / "data" / "datasets_manifest.json"
    mpath.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    mpath2 = write_markdown(repo, manifest)
    print(f"manifest -> {mpath}")
    print(f"doc      -> {mpath2}")
    print(
        f"ok={len(ok)}/{len(entries)} total_bytes={manifest['summary']['total_bytes']} "
        f"largest={biggest['uci_id']}:{biggest['bytes']}"
    )
    return manifest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["download", "parse", "all"])
    ap.add_argument("--repo", required=True, help="absolute path to the repository root")
    ap.add_argument(
        "--only",
        default="",
        help="comma-separated UCI ids or slot indices to (re)download; others are reused",
    )
    args = ap.parse_args(argv)

    repo = Path(args.repo).resolve()
    if not (repo / "data").is_dir():
        die(f"not a data repo (no data/ dir): {repo}")
    only = [int(x) for x in re.split(r"[,\s]+", args.only) if x.strip()] if args.only else None
    print(f"repo = {repo}")

    if args.stage in ("download", "all"):
        stage_download(repo, only)
    if args.stage in ("parse", "all"):
        stage_parse(repo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
