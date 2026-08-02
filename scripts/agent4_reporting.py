# -*- coding: utf-8 -*-
"""Agent 4: 실행 결과 분석, Checkpoint 4 검증, Slack/Notion 보고.

처리 순서
1. reports/qa_results.json과 reports/report.html 파싱
2. Checkpoint 4에서 결과 수, 테스트 ID, 상태, 분류 정합성 검증
3. 실제 실행 결과와 릴리즈 판정 계산
4. 검증된 결과만 Slack과 Notion으로 전송

중요
- Failed는 원인과 관계없이 실제 실행 결과 FAILED로 유지한다.
- 환경 문제는 실패의 원인 분류일 뿐 성공으로 바꾸지 않는다.
- Checkpoint 4의 VALIDATED는 데이터 정합성 확인 완료를 뜻한다.
"""

import argparse
import html
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass


REPORTS_DIR = ROOT_DIR / "reports"
RESULTS_PATH = REPORTS_DIR / "qa_results.json"
HTML_REPORT_PATH = REPORTS_DIR / "report.html"
SUMMARY_PATH = REPORTS_DIR / "agent4_summary.json"
CHECKPOINT4_PATH = REPORTS_DIR / "checkpoint4_validation.json"
PORTFOLIO_PATH = ROOT_DIR / "project.html"
TRACEABILITY_PATH = ROOT_DIR / "docs" / "samples" / "traceability_matrix.md"
NOTION_REQUEST_TIMEOUT = 30

PYTEST_STATUSES = {
    "passed", "failed", "skipped", "error", "xfailed", "xpassed", "rerun"
}

# conftest.py와 동일하게 유지: HTML 요약 카운트에서 제외되는 TC 목록
# TC-ENV-000은 사전 환경 검증(Pre-check) 단계이며 비즈니스 TC가 아닙니다.
EXCLUDED_FROM_SUMMARY = {"TC-ENV-000"}

# 테스트 우선순위는 실행 결과가 아니라 기능 중요도와 장애 영향 범위로 결정한다.
# P1: 핵심 제어, 안전·제어 차단, 다중 장비 영향 또는 릴리즈 차단 결함
# P2: 환경 점검, 보조 도메인 규칙, 경계값 및 파이프라인 분류 검증
P1_TEST_CASES = {
    "TC-MODE-001",
    "TC-LOCK-001",
    "TC-ERR-001",
    "TC-INT-002",
    "TC-TEMP-002",
}

QA_CLASSIFICATIONS = {
    "product_defect": "제품 결함 후보",
    "requirement_review": "요구사항 확인 필요",
    "environment_issue": "환경·시뮬레이터 문제",
    "automation_issue": "자동화 코드 문제",
    "not_executed": "조건 부족으로 미실행",
    "none": "분류 없음",
}

CLASSIFICATION_RULES = [
    (re.compile(r"제품\s*결함|product\s*defect", re.I), "product_defect"),
    (re.compile(r"기획|요구사항|requirement|spec", re.I), "requirement_review"),
    (re.compile(r"자동화\s*코드|selector|locator|assert|wait|playwright", re.I), "automation_issue"),
    (re.compile(r"환경|시뮬레이터|timeout|network|browser", re.I), "environment_issue"),
    (re.compile(r"미실행|조건\s*부족|not[_ -]?run|blocked", re.I), "not_executed"),
]

# 이 표는 상태와 분류의 논리적 조합만 검증한다.
# 예: failed + environment_issue는 유효한 분류 조합이지만 실행 결과는 FAILED다.
ALLOWED_STATUS_CLASSIFICATIONS = {
    "passed": {"none"},
    "failed": {"product_defect", "environment_issue", "automation_issue"},
    "error": {"environment_issue", "automation_issue"},
    "skipped": {"requirement_review", "not_executed"},
    "xfailed": {"product_defect", "environment_issue", "automation_issue", "not_executed"},
    "xpassed": {"automation_issue"},
    "rerun": {"environment_issue", "automation_issue"},
}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def classify_result(result: dict[str, Any]) -> str:
    """Pytest 상태를 바꾸지 않고 failure_reason만 5가지 원인으로 분류한다."""
    status = str(result.get("result", "")).strip().lower()
    reason = str(result.get("failure_reason", "") or "").strip()
    if status == "passed":
        return "none"
    for pattern, classification in CLASSIFICATION_RULES:
        if pattern.search(reason):
            return classification
    return "none"


def parse_report(path: Path = RESULTS_PATH) -> list[dict[str, Any]]:
    """기존 Agent 4의 parse_report 역할을 유지해 qa_results.json을 읽는다."""
    if not path.exists():
        raise FileNotFoundError(f"결과 JSON을 찾을 수 없습니다: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("qa_results.json 최상위 구조는 배열이어야 합니다.")

    normalized: list[dict[str, Any]] = []
    for row in data:
        if not isinstance(row, dict):
            normalized.append({"_invalid_row": row})
            continue

        item = dict(row)
        item["test_id"] = str(item.get("test_id", "")).strip()
        item["description"] = str(item.get("description", "") or "").strip()
        item["result"] = str(item.get("result", "")).strip().lower()
        item["failure_reason"] = str(item.get("failure_reason", "") or "").strip()
        item["qa_classification"] = classify_result(item)
        normalized.append(item)

    return normalized


def parse_html_report(path: Path = HTML_REPORT_PATH) -> dict[str, Any]:
    """pytest-html의 data-jsonblob에서 원본 실행 결과를 읽는다."""
    if not path.exists():
        raise FileNotFoundError(f"HTML Report를 찾을 수 없습니다: {path}")

    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    container = soup.find(id="data-container")
    if container is None or not container.get("data-jsonblob"):
        raise ValueError("report.html에서 pytest-html data-jsonblob을 찾을 수 없습니다.")

    payload = json.loads(container.get("data-jsonblob"))
    rows: list[dict[str, str]] = []

    for node_id, attempts in payload.get("tests", {}).items():
        for attempt in attempts:
            rows.append(
                {
                    "test_id": node_id.split("::")[-1],
                    "result": str(attempt.get("result", "")).lower(),
                    "description": str(attempt.get("description", "")),
                    "failure_reason": str(attempt.get("failure", "")),
                }
            )

    return {
        "title": payload.get("title", ""),
        "rows": rows,
        "counts": dict(Counter(row["result"] for row in rows)),
        "total": len(rows),
    }


def checkpoint4_validate(
    results: list[dict[str, Any]], html_report: dict[str, Any]
) -> dict[str, Any]:
    """외부 보고 전에 JSON, HTML Report, 원인 분류의 정합성을 검증한다."""
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    required_fields = {"test_id", "description", "result", "failure_reason"}
    json_ids: list[str] = []

    for index, row in enumerate(results, start=1):
        if "_invalid_row" in row:
            errors.append({"code": "CP4-001", "message": f"JSON {index}번째 항목이 객체가 아닙니다."})
            continue

        missing = [field for field in required_fields if field not in row]
        if missing:
            errors.append({"code": "CP4-002", "message": f"{index}번째 항목 필수 필드 누락: {', '.join(missing)}"})

        test_id = row.get("test_id", "")
        status = row.get("result", "")
        classification = row.get("qa_classification", "none")
        json_ids.append(test_id)

        if not test_id:
            errors.append({"code": "CP4-003", "message": f"{index}번째 항목 test_id가 비어 있습니다."})

        if status not in PYTEST_STATUSES:
            errors.append({"code": "CP4-004", "message": f"{test_id or index}: 허용되지 않은 Pytest 상태 '{status}'"})
            continue

        if classification not in ALLOWED_STATUS_CLASSIFICATIONS.get(status, set()):
            errors.append(
                {
                    "code": "CP4-005",
                    "message": f"{test_id}: 상태 '{status}'와 QA 분류 '{classification}' 조합을 확인하세요.",
                }
            )

        if status != "passed" and not row.get("failure_reason"):
            errors.append({"code": "CP4-006", "message": f"{test_id}: 비통과 결과에 failure_reason이 없습니다."})

    duplicates = [test_id for test_id, count in Counter(json_ids).items() if test_id and count > 1]
    if duplicates:
        errors.append({"code": "CP4-007", "message": f"중복 test_id: {', '.join(duplicates)}"})

    html_rows = html_report.get("rows", [])
    json_map = {row.get("test_id", ""): row for row in results if row.get("test_id")}
    html_map = {row.get("test_id", ""): row for row in html_rows if row.get("test_id")}

    missing_in_html = sorted(set(json_map) - set(html_map))
    missing_in_json = sorted(set(html_map) - set(json_map))
    if missing_in_html:
        errors.append({"code": "CP4-008", "message": f"JSON에만 존재하는 결과: {', '.join(missing_in_html)}"})
    if missing_in_json:
        errors.append({"code": "CP4-009", "message": f"HTML Report에만 존재하는 결과: {', '.join(missing_in_json)}"})

    for test_id in sorted(set(json_map) & set(html_map)):
        json_status = json_map[test_id]["result"]
        html_status = html_map[test_id]["result"]
        if json_status != html_status:
            errors.append(
                {
                    "code": "CP4-010",
                    "message": f"{test_id}: JSON 상태 '{json_status}'와 HTML 상태 '{html_status}'가 다릅니다.",
                }
            )

    json_counts = dict(Counter(row.get("result", "") for row in results))
    html_counts = html_report.get("counts", {})

    # TC-ENV-000과 같이 HTML 요약에서 의도적으로 제외된 TC를 고려한 총 수 검증
    # 주의: EXCLUDED_FROM_SUMMARY는 HTML 상단 '요약 문구(run-count)'의 표시 수치에만 영향을 줍니다.
    # data-jsonblob의 실제 결과 행(total)은 TC-ENV-000 포함 전체 건수이므로, JSON과 반드시 1:1 일치해야 합니다.
    if len(results) != html_report.get("total", 0):
        errors.append(
            {
                "code": "CP4-011",
                "message": f"총 결과 수 불일치: JSON={len(results)}, HTML={html_report.get('total', 0)}",
            }
        )


    if json_counts != html_counts:
        errors.append(
            {
                "code": "CP4-012",
                "message": f"상태별 집계 불일치: JSON={json_counts}, HTML={html_counts}",
            }
        )

    # pytest-html의 화면 요약 문구(run-count)와 HTML 실제 결과 행 수(total) 비교
    # pytest-html의 run-count는 기본적으로 skipped, xfailed를 제외한 실제 실행(passed+failed+error) 건수를 의미합니다.
    try:
        report_text = HTML_REPORT_PATH.read_text(encoding="utf-8")
        match = re.search(r'<p class="run-count">\s*(\d+) tests? took', report_text)
        if match:
            html_summary_count = int(match.group(1))
            html_actual_count = html_report.get("total", 0)

            # 실제 실행 건수 = 전체 건수 - (skipped + xfailed)
            skipped_count = sum(1 for r in results if r.get("result") in ("skipped", "xfailed"))
            expected_run_count = html_actual_count - skipped_count

            if html_summary_count != expected_run_count:
                warnings.append(
                    {
                        "code": "CP4-W01",
                        "message": (
                            f"pytest-html Summary 문구({html_summary_count})가 예상되는 실행 건수"
                            f"({expected_run_count})와 다릅니다. 실제 결과 행과 JSON 수치를 사용하세요."
                        ),
                    }
                )
    except OSError:
        pass

    return {
        "checkpoint": "Checkpoint 4",
        "status": "VALIDATED" if not errors else "BLOCKED",
        "validated_at": now_iso(),
        "external_reporting_allowed": not errors,
        "json_total": len(results),
        "html_total": html_report.get("total", 0),
        "errors": errors,
        "warnings": warnings,
    }


def determine_execution_result(status_counts: Counter) -> str:
    """Failed/Error가 하나라도 있으면 원인과 관계없이 FAILED다."""
    if status_counts.get("failed", 0) > 0 or status_counts.get("error", 0) > 0:
        return "FAILED"

    if (
        status_counts.get("skipped", 0) > 0
        or status_counts.get("xfailed", 0) > 0
        or status_counts.get("rerun", 0) > 0
    ):
        return "INCOMPLETE"

    return "PASSED"


def determine_release_decision(
    execution_result: str, classification_counts: Counter, checkpoint_status: str
) -> str:
    """환경 문제도 실패이므로 릴리즈 통과로 보지 않고 HOLD 처리한다."""
    if checkpoint_status != "VALIDATED":
        return "HOLD"
    if execution_result != "PASSED":
        return "HOLD"
    if classification_counts.get("requirement_review", 0) > 0:
        return "HOLD"
    if classification_counts.get("not_executed", 0) > 0:
        return "HOLD"
    return "PASS"


def build_summary(results: list[dict[str, Any]], validation: dict[str, Any]) -> dict[str, Any]:
    status_counts = Counter(row.get("result", "") for row in results)
    classification_counts = Counter(row.get("qa_classification", "none") for row in results)
    execution_result = determine_execution_result(status_counts)
    release_decision = determine_release_decision(
        execution_result, classification_counts, validation["status"]
    )

    return {
        "run_id": "RUN-" + datetime.now().strftime("%Y%m%d-%H%M%S"),
        "generated_at": now_iso(),
        "source": {
            "results_json": RESULTS_PATH.name,
            "html_report": HTML_REPORT_PATH.name,
        },
        "checkpoint4": {
            "status": validation["status"],
            "external_reporting_allowed": validation["external_reporting_allowed"],
            "warning_count": len(validation["warnings"]),
            "error_count": len(validation["errors"]),
        },
        "execution": {
            "result": execution_result,
            "release_decision": release_decision,
        },
        "pytest_summary": {
            "total": len(results),
            **{status: status_counts.get(status, 0) for status in sorted(PYTEST_STATUSES)},
        },
        "qa_classification_summary": {
            key: classification_counts.get(key, 0) for key in QA_CLASSIFICATIONS
        },
        "results": results,
    }


def format_slack_payload(report_data: dict[str, Any]) -> dict[str, Any]:
    """풍부한 포맷(Block Kit)을 사용하여 Slack 메시지를 구성합니다."""
    pytest_summary = report_data["pytest_summary"]
    qa_summary = report_data["qa_classification_summary"]

    execution_result = report_data['execution']['result']
    release_decision = report_data['execution']['release_decision']

    if release_decision == "PASS":
        decision_text = "🟢 *PASS (배포 승인)* - 모든 검증 통과 완료"
    elif execution_result == "INCOMPLETE":
        decision_text = "🟡 *HOLD* - 일부 테스트 미실행 또는 요구사항 확인 필요"
    else:
        decision_text = "🔴 *HOLD* - 비통과·미실행 또는 요구사항 확인 항목이 존재해 릴리즈 검토가 필요합니다."

    total = pytest_summary.get('total', 0)
    passed = pytest_summary.get('passed', 0)
    failed = pytest_summary.get('failed', 0) + pytest_summary.get('error', 0)
    skipped = pytest_summary.get('skipped', 0) + pytest_summary.get('xfailed', 0)

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📊 [가상 관제 시스템] QA 파이프라인 자동화 리포트",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*최종 릴리즈 판정*: {decision_text}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"""*총 테스트 수*: {total}건
✅ *S/W Pass*: {passed}건
🚨 *S/W Fail*: {failed}건
⚠️ *Skipped*: {skipped}건"""
            }
        },
        {"type": "divider"}
    ]

    class_map = {
        "product_defect": {"emoji": "🔴", "title": "1. 제품 결함 후보 (Product Defect)"},
        "requirement_review": {"emoji": "⚠️", "title": "2. 기획·요구사항 확인 필요 (Requirement Review Needed)"},
        "environment_issue": {"emoji": "🔌", "title": "3. 테스트 환경·시뮬레이터 문제 (Test Env / Simulator Issue)"},
        "automation_issue": {"emoji": "🤖", "title": "4. 자동화 코드 문제 (Automation Script Error)"},
        "not_executed": {"emoji": "🚧", "title": "5. 조건 부족으로 미실행 (Not Executed)"}
    }

    grouped_results = {}
    for res in report_data.get('results', []):
        cls = res.get('qa_classification', 'none')
        if cls == 'none' or res.get('result') == 'passed':
            continue
        if cls not in grouped_results:
            grouped_results[cls] = []
        grouped_results[cls].append(res)

    for cls_key, info in class_map.items():
        items = grouped_results.get(cls_key, [])
        if not items:
            continue

        text_lines = [f"{info['emoji']} *{info['title']}*"]

        for item in items:
            test_id = item.get('test_id', 'Unknown')
            if "::" in test_id:
                test_id = test_id.split("::")[-1]
            desc = item.get('description', '')
            desc = re.sub(r'^\[TC-[^\]]+\]\s*', '', desc)
            desc = re.sub(r'\s*—\s*Finding:\s*[A-Z0-9-]+', '', desc)
            reason = item.get('failure_reason', '상세 사유 없음')
            text_lines.append(f"> *[{item.get('tc_id', test_id)}]* {desc}\n> └─ 상세 사유: {reason}")

        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "\n".join(text_lines)
            }
        })

    blocks.append({"type": "divider"})

    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"""*테스트 환경*: Virtual Central Controller Simulator
*실행 일시*: {report_data.get('generated_at', '')}
*자동화 엔진*: Playwright v1.40+
*Run ID*: {report_data.get('run_id', '')}
*외부 전송*: 기본 Dry-run / `--send`에서 Slack·Notion API 호출"""
            }
        ]
    })

    return {"blocks": blocks}

def send_to_slack(payload: dict[str, Any], *, dry_run: bool = True) -> bool:
    """검증된 결과만 Slack Webhook으로 전송한다."""
    if dry_run:
        print("[DRY-RUN] Slack payload 미리보기 (외부 전송 없음)")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return False

    webhook_url = os.getenv("SLACK_WEBHOOK_URL", "").strip()
    if not webhook_url or "여기에" in webhook_url:
        print("[INFO] SLACK_WEBHOOK_URL 미설정: Slack payload 콘솔 미리보기")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return False

    response = requests.post(webhook_url, json=payload, timeout=15)
    response.raise_for_status()
    return True


def send_to_notion(report_data: dict[str, Any], *, dry_run: bool = True) -> bool:
    """실행 요약 및 개별 TC 결과를 Notion DB에 Upsert (TC ID 기반 업데이트) 한다.

    [구현 목적]
    - 매 실행마다 중복 페이지를 생성하지 않고, TC ID를 기준으로 기존 페이지를 찾아 상태(결과, 로그 등)만 업데이트(PATCH) 합니다.
    - 기존에 없는 TC라면 새 페이지를 생성(POST) 합니다.
    """
    if dry_run:
        print("[DRY-RUN] Notion TC-ID 기반 Upsert 미리보기 (외부 변경 없음)")
        for tc in report_data.get("results", []):
            print(
                f"       - [UPSERT] {tc.get('tc_id', 'UNKNOWN')} | "
                f"Status: {str(tc.get('result', '')).upper()} | "
                f"Classification: {tc.get('qa_classification', 'none')}"
            )
        return False

    notion_token = os.getenv("NOTION_API_KEY", "").strip()
    data_source_id = os.getenv("NOTION_DATA_SOURCE_ID", "").strip()

    if not notion_token or not data_source_id:
        print("[INFO] Notion 환경변수 미설정(NOTION_API_KEY, NOTION_DATA_SOURCE_ID): Notion TC-ID 기반 Upsert 시뮬레이션(콘솔 미리보기)")

        # 1. qa_results.json의 테스트 결과를 불러옵니다.
        try:
            results_path = Path("reports/qa_results.json")
            results = json.loads(results_path.read_text(encoding="utf-8")) if results_path.exists() else []
        except Exception as e:
            print(f"       JSON 결과 로드 실패: {e}")
            results = []

        print(f"       총 {len(results)}개의 TC에 대해 Upsert(수정/추가)를 시뮬레이션합니다.")

        # 2. 각 TC별로 Upsert 로직 (시뮬레이션 출력)
        for tc in results:
            tc_id = tc.get("tc_id", "UNKNOWN")
            result = tc.get("result", "")
            finding_type = tc.get("qa_classification", "none")

            # 실제 API 호출이라면 아래와 같이 동작합니다.
            # 2-1) Notion Query API (filter: TC-ID == tc_id)
            # 2-2) 결과(results)가 있으면 -> PATCH (업데이트)
            # 2-3) 결과(results)가 없으면 -> POST (신규 생성)

            action = "PATCH (Update)" if tc_id.startswith("TC-") else "POST (Create)"
            print(f"       - [{action}] {tc_id} | Status: {result.upper()} | Finding: {finding_type}")

        print("       Notion 전송 시뮬레이션 완료.")
        return False

    # 실제 Notion 연동 로직 (환경변수 존재 시 동작)
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2026-03-11",
        "Content-Type": "application/json",
    }

    # 1. 검증된 파이프라인 데이터에서 결과 로드
    results = report_data.get("results", [])
    if not results:
        return False

    # 2. 개별 TC Upsert
    success = True
    for tc in results:
        tc_id = tc.get("tc_id")
        if not tc_id:
            continue

        # (1) 페이지 존재 여부 쿼리
        query_payload = {
            "filter": {
                "property": "TC-ID",
                "title": {"equals": tc_id}
            }
        }
        resp = requests.post(
            f"https://api.notion.com/v1/data_sources/{data_source_id}/query",
            headers=headers,
            json=query_payload,
            timeout=NOTION_REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            print(f"[ERROR] Notion Query 실패 ({tc_id}): HTTP {resp.status_code} {resp.text[:300]}")
            success = False
            continue

        query_results = resp.json().get("results", [])

        # (2) 속성 정의
        status_map = {
            "passed": "Pass",
            "failed": "Fail",
            "skipped": "Review Needed",
            "error": "Blocker"
        }
        notion_status = status_map.get(tc.get("result", "").lower(), "Blocked")

        desc = tc.get("description", "")
        # 구분 자동 판별 로직
        category = "엣지케이스"
        if tc_id == "TC-ENV-000":
            category = "사전 점검"
        elif "해피패스" in desc:
            category = "해피패스"
        elif "결함" in desc or "예외" in desc or tc.get("result") == "failed":
            category = "예외/결함"

        # 기능 중요도와 장애 영향 범위에 따른 명시적 우선순위
        priority = "P1" if tc_id in P1_TEST_CASES else "P2"

        # 앞의 숫자 제거 ("1. 제품 결함 후보" -> "제품 결함 후보")
        raw_reason = tc.get("failure_reason", "")
        clean_reason = re.sub(r'^\d+\.\s*', '', raw_reason)

        # Pass 인 경우 '결과' 컬럼에 '정상 동작' 명시
        if tc.get("result") == "passed" and not clean_reason:
            clean_reason = "정상 동작"

        # 테스트 제목에서 [TC-XXX] 접두사 제거
        clean_desc = re.sub(r'^\[TC-[^\]]+\]\s*', '', desc)

        # 불필요한 영문 텍스트 및 꼬리표(Finding: ...) 제거
        clean_desc = re.sub(r'\s*—\s*Finding:\s*[A-Z0-9-]+', '', clean_desc)
        clean_desc = clean_desc.replace('Playwright TimeoutError', '시간 초과 오류 발생')
        clean_desc = clean_desc.replace('(Simulator Timeout)', '').strip()

        properties = {
            "TC-ID": {"title": [{"text": {"content": tc_id}}]},
            "테스트 제목": {"rich_text": [{"text": {"content": clean_desc[:2000]}}]},
            "실행 결과": {"select": {"name": notion_status}},
            "결과 ": {"rich_text": [{"text": {"content": clean_reason[:2000]}}]},
            "구분": {"select": {"name": category}},
            "우선 순위": {"select": {"name": priority}}
        }

        # (3) Upsert 분기
        if query_results:
            page_id = query_results[0]["id"]
            mutation_response = requests.patch(
                f"https://api.notion.com/v1/pages/{page_id}",
                headers=headers,
                json={"properties": properties},
                timeout=NOTION_REQUEST_TIMEOUT,
            )
        else:
            mutation_response = requests.post(
                "https://api.notion.com/v1/pages",
                headers=headers,
                json={
                    "parent": {
                        "type": "data_source_id",
                        "data_source_id": data_source_id,
                    },
                    "properties": properties,
                },
                timeout=NOTION_REQUEST_TIMEOUT,
            )

        if not mutation_response.ok:
            print(
                f"[ERROR] Notion Upsert 실패 ({tc_id}): "
                f"HTTP {mutation_response.status_code} {mutation_response.text[:300]}"
            )
            success = False

    return success


def sync_portfolio_outputs(report_data: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    """최신 실행 결과를 Section 7과 추적성 문서에 동기화한다."""
    portfolio = PORTFOLIO_PATH.read_text(encoding="utf-8")
    status_view = {
        "passed": ("result-pass", "Pass"),
        "failed": ("badge-fail", "Fail"),
        "skipped": ("result-review", "Review Needed"),
        "error": ("badge-fail", "Error"),
    }

    for result in report_data:
        tc_id = result["tc_id"]
        row_pattern = re.compile(
            rf'(<tr class="tc-row"[^>]*>\s*<td[^>]*>{re.escape(tc_id)}</td>.*?</tr>)',
            re.S,
        )
        row_match = row_pattern.search(portfolio)
        if not row_match:
            raise ValueError(f"Section 7에서 {tc_id} 행을 찾을 수 없습니다.")

        row = row_match.group(1)
        css_class, label = status_view.get(result["result"], ("result-review", result["result"]))
        row, status_count = re.subn(
            r'<span class="(?:result|badge)-[^"]+">[^<]+</span>',
            f'<span class="{css_class}">{label}</span>',
            row,
            count=1,
        )
        executed_date = str(result["executed_at"])[:10]
        row, date_count = re.subn(
            r'(<td style="color:#94a3b8; font-size:11px;">)[^<]+(</td>)',
            rf'\g<1>{executed_date}\g<2>',
            row,
            count=1,
        )
        if status_count != 1 or date_count != 1:
            raise ValueError(f"Section 7의 {tc_id} 상태/실행일 형식이 예상과 다릅니다.")
        portfolio = portfolio[:row_match.start()] + row + portfolio[row_match.end():]

        duration_pattern = re.compile(
            rf'(<td[^>]*>{re.escape(tc_id)}</td>.*?<tr class="tc-details".*?실행 시간\s+)([0-9.]+)(초)',
            re.S,
        )
        portfolio, duration_count = duration_pattern.subn(
            rf'\g<1>{result["duration"]}\g<3>', portfolio, count=1
        )
        if duration_count != 1:
            raise ValueError(f"Section 7의 {tc_id} 실행시간을 찾을 수 없습니다.")

    PORTFOLIO_PATH.write_text(portfolio, encoding="utf-8")

    trace = TRACEABILITY_PATH.read_text(encoding="utf-8")
    source_run_ids = {row["run_id"] for row in report_data}
    if len(source_run_ids) != 1:
        raise ValueError("qa_results.json의 Source Run ID가 단일 값이 아닙니다.")
    source_run_id = next(iter(source_run_ids))
    agent_run_id = summary["run_id"]
    trace, source_count = re.subn(
        r'(- \*\*Source Test Run ID\*\*: `)[^`]+(`)',
        rf'\g<1>{source_run_id}\g<2>',
        trace,
        count=1,
    )
    trace, agent_count = re.subn(
        r'(- \*\*Agent 4 Analysis Run ID\*\*: `)[^`]+(`)',
        rf'\g<1>{agent_run_id}\g<2>',
        trace,
        count=1,
    )
    if source_count != 1 or agent_count != 1:
        raise ValueError("추적성 문서의 Run ID 표식을 찾을 수 없습니다.")
    TRACEABILITY_PATH.write_text(trace, encoding="utf-8")

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Agent 4 결과 분석 및 외부 보고")
    parser.add_argument(
        "--send",
        action="store_true",
        help="검증 통과 후 Slack/Notion에 실제 전송합니다. 기본값은 Dry-run입니다.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    mode = "LIVE SEND" if args.send else "DRY-RUN"
    print(f"\n[Agent 4] 결과 분석 및 Checkpoint 4 검증 시작 ({mode})\n")

    try:
        report_data = parse_report()
        html_report = parse_html_report()
        validation = checkpoint4_validate(report_data, html_report)
        write_json(CHECKPOINT4_PATH, validation)

        summary = build_summary(report_data, validation)
        write_json(SUMMARY_PATH, summary)
        sync_portfolio_outputs(report_data, summary)

        print(f"[Checkpoint 4 데이터 검증] {validation['status']}")
        print(f"[실제 실행 결과] {summary['execution']['result']}")
        print(f"[릴리즈 판정] {summary['execution']['release_decision']}")
        print(f"[OK] 검증 결과 저장: {CHECKPOINT4_PATH}")
        print(f"[OK] Agent 4 요약 저장: {SUMMARY_PATH}")

        if not validation["external_reporting_allowed"]:
            print("[BLOCKED] 결과 불일치로 Slack·Notion 보고를 중단합니다.")
            for error in validation["errors"]:
                print(f"  - {error['code']}: {error['message']}")
            return 2

        for warning in validation["warnings"]:
            print(f"[WARNING] {warning['code']}: {warning['message']}")

        slack_sent = send_to_slack(format_slack_payload(summary), dry_run=not args.send)
        notion_sent = send_to_notion(summary, dry_run=not args.send)

        print(f"[Agent 4] Slack 전송: {'완료' if slack_sent else '생략/미리보기'}")
        print(f"[Agent 4] Notion 전송: {'완료' if notion_sent else '생략'}")
        return 0

    except Exception as exc:
        failure = {
            "checkpoint": "Checkpoint 4",
            "status": "BLOCKED",
            "validated_at": now_iso(),
            "external_reporting_allowed": False,
            "errors": [{"code": "CP4-999", "message": str(exc)}],
            "warnings": [],
        }
        write_json(CHECKPOINT4_PATH, failure)
        print(f"[ERROR] Agent 4 실행 실패: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
