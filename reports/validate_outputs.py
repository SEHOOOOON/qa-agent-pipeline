#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""파이프라인 산출물 전체 교차 검증 스크립트"""

import json
import sys
from pathlib import Path
from collections import Counter

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: beautifulsoup4 not installed")
    sys.exit(1)

REPORTS = Path(__file__).parent
ROOT = REPORTS.parent

html_path = REPORTS / "report.html"
json_path = REPORTS / "qa_results.json"
summary_path = REPORTS / "agent4_summary.json"
cp4_path = REPORTS / "checkpoint4_validation.json"

issues = []

# ── 1. HTML Report 파싱 ──
print("=" * 60)
print("[1] HTML Report (data-jsonblob)")
print("=" * 60)
soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
container = soup.find(id="data-container")
blob = json.loads(container.get("data-jsonblob"))

html_rows = []
for node_id, attempts in blob.get("tests", {}).items():
    for attempt in attempts:
        html_rows.append({
            "test_id": node_id.split("::")[-1],
            "result": str(attempt.get("result", "")).lower(),
        })

print(f"  Title: {blob.get('title', 'N/A')}")
print(f"  Total rows: {len(html_rows)}")
for r in html_rows:
    print(f"    {r['test_id']:60s} {r['result']}")

# ── 2. qa_results.json ──
print()
print("=" * 60)
print("[2] qa_results.json")
print("=" * 60)
json_data = json.loads(json_path.read_text(encoding="utf-8"))
print(f"  Total: {len(json_data)}")
for r in json_data:
    reason = r.get("failure_reason") or "-"
    print(f"    {r['tc_id']:15s} {r['result']:8s} | {reason:30s}")

# ── 3. JSON ↔ HTML 교차 검증 ──
print()
print("=" * 60)
print("[3] JSON <-> HTML Cross Validation")
print("=" * 60)
json_map = {r["test_id"]: r["result"] for r in json_data}
html_map = {r["test_id"]: r["result"] for r in html_rows}

for tid in sorted(set(json_map) | set(html_map)):
    j = json_map.get(tid, "MISSING_IN_JSON")
    h = html_map.get(tid, "MISSING_IN_HTML")
    match = "OK" if j == h else "MISMATCH"
    if j != h:
        issues.append(f"[3] {tid}: JSON={j}, HTML={h}")
    print(f"    {tid:60s} JSON={j:8s} HTML={h:8s} [{match}]")

# ── 4. 5종 분류 정합성 ──
print()
print("=" * 60)
print("[4] QA Classification Engine")
print("=" * 60)

EXPECTED = {
    "TC-PIPE-001": ("skipped", "requirement_review"),
    "TC-PIPE-002": ("failed", "environment_issue"),
    "TC-PIPE-003": ("failed", "automation_issue"),
    "TC-PIPE-004": ("skipped", "not_executed"),
    "TC-TEMP-002": ("failed", "product_defect"),
}

summary = json.loads(summary_path.read_text(encoding="utf-8"))
summary_results = {r["tc_id"]: r for r in summary.get("results", [])}

for tc_id, (exp_status, exp_class) in EXPECTED.items():
    row = summary_results.get(tc_id, {})
    actual_status = row.get("result", "MISSING")
    actual_class = row.get("qa_classification", "MISSING")
    status_ok = actual_status == exp_status
    class_ok = actual_class == exp_class
    mark = "OK" if (status_ok and class_ok) else "FAIL"
    if not (status_ok and class_ok):
        issues.append(f"[4] {tc_id}: expected ({exp_status}, {exp_class}), got ({actual_status}, {actual_class})")
    print(f"    {tc_id:15s} status={actual_status:8s}({'OK' if status_ok else 'NG'}) class={actual_class:20s}({'OK' if class_ok else 'NG'}) [{mark}]")

# ── 5. Checkpoint 4 검증 ──
print()
print("=" * 60)
print("[5] Checkpoint 4 Validation")
print("=" * 60)
cp4 = json.loads(cp4_path.read_text(encoding="utf-8"))
print(f"  Status:   {cp4['status']}")
print(f"  JSON:     {cp4['json_total']}")
print(f"  HTML:     {cp4['html_total']}")
print(f"  Errors:   {len(cp4['errors'])}")
print(f"  Warnings: {len(cp4['warnings'])}")

if cp4["json_total"] != cp4["html_total"]:
    issues.append(f"[5] CP4 total mismatch: JSON={cp4['json_total']}, HTML={cp4['html_total']}")
if cp4["json_total"] != len(json_data):
    issues.append(f"[5] CP4 json_total({cp4['json_total']}) != actual JSON count({len(json_data)})")
if cp4["errors"]:
    issues.append(f"[5] CP4 has {len(cp4['errors'])} errors")

# ── 6. Agent 4 Summary ──
print()
print("=" * 60)
print("[6] Agent 4 Summary")
print("=" * 60)
print(f"  Run ID:     {summary['run_id']}")
print(f"  CP4:        {summary['checkpoint4']['status']}")
print(f"  Execution:  {summary['execution']['result']}")
print(f"  Release:    {summary['execution']['release_decision']}")
print(f"  Pytest:     {summary['pytest_summary']}")
print(f"  QA Classes: {summary['qa_classification_summary']}")

# Release Decision 로직 검증
exec_result = summary["execution"]["result"]
release = summary["execution"]["release_decision"]
if exec_result == "FAILED" and release != "HOLD":
    issues.append(f"[6] Execution=FAILED but Release={release} (should be HOLD)")
if exec_result == "PASSED" and summary["qa_classification_summary"].get("requirement_review", 0) > 0 and release != "HOLD":
    issues.append(f"[6] requirement_review exists but Release={release} (should be HOLD)")

# ── 7. Run ID 일관성 ──
print()
print("=" * 60)
print("[7] Run ID Consistency")
print("=" * 60)
run_ids = set(r["run_id"] for r in json_data)
print(f"  Unique run_ids: {run_ids}")
if len(run_ids) == 1:
    print("  OK: All records share the same run_id")
else:
    issues.append(f"[7] Multiple run_ids found: {run_ids}")

# ── 8. Description ↔ TC ID 매핑 ──
print()
print("=" * 60)
print("[8] Description <-> TC ID Mapping")
print("=" * 60)
import re
for r in json_data:
    desc = r.get("description", "")
    match = re.search(r"\[(TC-[^\]]+)\]", desc)
    desc_tc = match.group(1) if match else "NO_MATCH"
    field_tc = r.get("tc_id", "MISSING")
    ok = desc_tc == field_tc
    if not ok:
        issues.append(f"[8] tc_id field={field_tc} but description has [{desc_tc}]")
    print(f"    {field_tc:15s} desc=[{desc_tc}] {'OK' if ok else 'MISMATCH'}")

# ── FINAL ──
print()
print("=" * 60)
print("FINAL RESULT")
print("=" * 60)
if issues:
    print(f"  ISSUES FOUND: {len(issues)}")
    for i in issues:
        print(f"    - {i}")
else:
    print("  ALL CHECKS PASSED (0 issues)")
print()
