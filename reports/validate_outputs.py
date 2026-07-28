#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""파이프라인 산출물 전체 교차 검증 스크립트"""

import json
import sys
from pathlib import Path
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

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

# ── 9. Agent 4 Summary ↔ 원본 JSON 필드 검증 ──
print()
print("=" * 60)
print("[9] Agent 4 Summary <-> qa_results.json")
print("=" * 60)

summary_by_test = {row.get("test_id", ""): row for row in summary.get("results", [])}
json_by_test = {row.get("test_id", ""): row for row in json_data}
if set(summary_by_test) != set(json_by_test):
    issues.append("[9] Agent 4 results와 qa_results.json의 test_id 집합이 다릅니다.")

for test_id in sorted(set(summary_by_test) & set(json_by_test)):
    source = json_by_test[test_id]
    derived = summary_by_test[test_id]
    mismatched = [
        field
        for field in ("run_id", "tc_id", "description", "result", "failure_reason", "executed_at", "duration")
        if source.get(field) != derived.get(field)
    ]
    if mismatched:
        issues.append(f"[9] {test_id}: Agent 4 필드 불일치 {mismatched}")

expected_counts = Counter(row.get("result", "") for row in json_data)
summary_counts = summary.get("pytest_summary", {})
for status in ("passed", "failed", "skipped", "error", "xfailed", "xpassed", "rerun"):
    if summary_counts.get(status, 0) != expected_counts.get(status, 0):
        issues.append(
            f"[9] pytest_summary.{status}={summary_counts.get(status, 0)} "
            f"!= source {expected_counts.get(status, 0)}"
        )
print(f"  Compared results: {len(set(summary_by_test) & set(json_by_test))}")

# ── 10. Portfolio Section 5·7·13 검증 ──
print()
print("=" * 60)
print("[10] Portfolio index.html Consistency")
print("=" * 60)

portfolio_path = ROOT / "index.html"
portfolio_text = portfolio_path.read_text(encoding="utf-8")
portfolio = BeautifulSoup(portfolio_text, "html.parser")

required_fragments = [
    "13</b><span>전체 실행",
    "8</b><span>통과",
    "3</b><span>실패",
    "2</b><span>Skipped",
    "5</b><span>QA 원인 분류",
]
for fragment in required_fragments:
    if fragment not in portfolio_text:
        issues.append(f"[10] Section 5 필수 집계 누락: {fragment}")

forbidden_fragments = [
    "22건 중 1건 실패",
    "pytest.approx(26.0)",
    "3000ms 초과 타임아웃",
    "test_pipeline_003_automation_script_error_classification",
    "test_tc_temp_002_lower_limit_boundary",
]
for fragment in forbidden_fragments:
    if fragment in portfolio_text:
        issues.append(f"[10] index.html에 과거 표현 잔존: {fragment}")

results_section = portfolio.find("section", id="test-results")
if results_section is None:
    issues.append("[10] Section 7 #test-results를 찾을 수 없습니다.")
else:
    portfolio_rows = {}
    result_map = {"pass": "passed", "fail": "failed", "review needed": "skipped"}
    for row in results_section.select("tr.tc-row"):
        cells = row.find_all("td", recursive=False)
        if len(cells) < 7:
            continue
        tc_id = cells[0].get_text(" ", strip=True)
        result_text = cells[3].get_text(" ", strip=True).lower()
        details = row.find_next_sibling("tr")
        details_text = details.get_text(" ", strip=True) if details else ""
        duration_match = re.search(r"실행 시간\s+([0-9.]+)초", details_text)
        portfolio_rows[tc_id] = {
            "result": result_map.get(result_text, result_text),
            "date": cells[6].get_text(" ", strip=True),
            "duration": float(duration_match.group(1)) if duration_match else None,
        }

    json_by_tc = {row["tc_id"]: row for row in json_data}
    if set(portfolio_rows) != set(json_by_tc):
        issues.append("[10] Section 7 TC ID 집합이 qa_results.json과 다릅니다.")
    for tc_id in sorted(set(portfolio_rows) & set(json_by_tc)):
        page_row = portfolio_rows[tc_id]
        source = json_by_tc[tc_id]
        if page_row["result"] != source["result"]:
            issues.append(f"[10] {tc_id}: Section 7={page_row['result']} JSON={source['result']}")
        if page_row["duration"] != float(source["duration"]):
            issues.append(f"[10] {tc_id}: 실행시간 Section 7={page_row['duration']} JSON={source['duration']}")
        if page_row["date"] != str(source["executed_at"])[:10]:
            issues.append(f"[10] {tc_id}: 실행일 Section 7={page_row['date']} JSON={str(source['executed_at'])[:10]}")
    print(f"  Section 7 rows: {len(portfolio_rows)}")

if portfolio.find("section", id="docs") is None:
    issues.append("[10] Section 13 #docs가 없습니다.")

# ── 11. 추적성 문서 Run ID·함수명 검증 ──
print()
print("=" * 60)
print("[11] Traceability Matrix Consistency")
print("=" * 60)

trace_path = ROOT / "docs" / "samples" / "traceability_matrix.md"
trace_text = trace_path.read_text(encoding="utf-8")
source_run_ids = {row.get("run_id", "") for row in json_data}
if len(source_run_ids) != 1:
    issues.append(f"[11] Source Run ID가 하나가 아닙니다: {source_run_ids}")
else:
    source_run_id = next(iter(source_run_ids))
    if source_run_id not in trace_text:
        issues.append(f"[11] 추적성 문서에 최신 Source Run ID 누락: {source_run_id}")
if summary.get("run_id", "") not in trace_text:
    issues.append(f"[11] 추적성 문서에 최신 Agent 4 Run ID 누락: {summary.get('run_id', '')}")

required_functions = {
    row.get("test_id", "").split("[", 1)[0]
    for row in json_data
    if row.get("tc_id") != "TC-ENV-000"
}
for function_name in sorted(required_functions):
    if function_name and function_name not in trace_text:
        issues.append(f"[11] 추적성 문서 함수명 누락: {function_name}")
print("  Run IDs and function mappings checked")

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
sys.exit(1 if issues else 0)
