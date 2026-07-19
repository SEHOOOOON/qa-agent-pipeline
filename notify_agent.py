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

load_dotenv()
try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"
RESULTS_PATH = REPORTS_DIR / "qa_results.json"
HTML_REPORT_PATH = REPORTS_DIR / "report.html"
SUMMARY_PATH = REPORTS_DIR / "agent4_summary.json"
CHECKPOINT4_PATH = REPORTS_DIR / "checkpoint4_validation.json"

PYTEST_STATUSES = {
    "passed", "failed", "skipped", "error", "xfailed", "xpassed", "rerun"
}

# conftest.py와 동일하게 유지: HTML 요약 카운트에서 제외되는 TC 목록
# TC-ENV-000은 사전 환경 검증(Pre-check) 단계이며 비즈니스 TC가 아닙니다.
EXCLUDED_FROM_SUMMARY = {"TC-ENV-000"}

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
    (re.compile(r"환경|시뮬레이터|timeout|network|browser", re.I), "environment_issue"),
    (re.compile(r"자동화\s*코드|selector|locator|assert|wait|playwright", re.I), "automation_issue"),
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
    if status == "passed" and not reason:
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

    # pytest-html의 화면 요약 문구와 HTML 실제 결과 행 수 비교
    # 단, EXCLUDED_FROM_SUMMARY 만큼의 차이는 의도된 것이므로 경고를 발생시키지 않는다.
    try:
        report_text = HTML_REPORT_PATH.read_text(encoding="utf-8")
        match = re.search(r'<p class="run-count">\s*(\d+) tests? took', report_text)
        if match:
            html_summary_count = int(match.group(1))
            html_actual_count = html_report.get("total", 0)
            excluded_count = len([r for r in results if r.get("tc_id") in EXCLUDED_FROM_SUMMARY])
            expected_diff = excluded_count  # TC-ENV-000 등 제외 대상만큼의 차이는 허용
            actual_count_diff = abs(html_actual_count - html_summary_count)
            if html_summary_count != html_actual_count and actual_count_diff != expected_diff:
                warnings.append(
                    {
                        "code": "CP4-W01",
                        "message": (
                            f"pytest-html Summary 문구({html_summary_count})와 실제 결과 행"
                            f"({html_actual_count})이 다릅니다. 실제 결과 행과 JSON 수치를 사용하세요."
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
    execution_result: str, classification_counts: Counter
) -> str:
    """환경 문제도 실패이므로 릴리즈 통과로 보지 않고 HOLD 처리한다."""
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
    release_decision = determine_release_decision(execution_result, classification_counts)

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
    """기존 함수명을 유지하면서 검증·실행·릴리즈 판정을 분리해 표시한다."""
    pytest_summary = report_data["pytest_summary"]
    qa_summary = report_data["qa_classification_summary"]

    return {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "QA 자동화 실행 결과", "emoji": True},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Run ID*\n{report_data['run_id']}"},
                    {"type": "mrkdwn", "text": f"*Checkpoint 4 데이터 검증*\n{report_data['checkpoint4']['status']}"},
                    {"type": "mrkdwn", "text": f"*실제 실행 결과*\n{report_data['execution']['result']}"},
                    {"type": "mrkdwn", "text": f"*릴리즈 판정*\n{report_data['execution']['release_decision']}"},
                    {
                        "type": "mrkdwn",
                        "text": (
                            f"*Pytest*\nTotal {pytest_summary['total']} | "
                            f"Passed {pytest_summary['passed']} | "
                            f"Skipped {pytest_summary['skipped']} | Failed {pytest_summary['failed']}"
                        ),
                    },
                    {
                        "type": "mrkdwn",
                        "text": (
                            "*QA 분류*\n"
                            f"제품 {qa_summary['product_defect']} | "
                            f"요구사항 {qa_summary['requirement_review']} | "
                            f"환경 {qa_summary['environment_issue']} | "
                            f"코드 {qa_summary['automation_issue']} | "
                            f"미실행 {qa_summary['not_executed']}"
                        ),
                    },
                ],
            },
        ]
    }


def send_to_slack(payload: dict[str, Any]) -> bool:
    """검증된 결과만 Slack Webhook으로 전송한다."""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL", "").strip()
    if not webhook_url or "여기에" in webhook_url:
        print("[INFO] SLACK_WEBHOOK_URL 미설정: Slack payload 콘솔 미리보기")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return False

    response = requests.post(webhook_url, json=payload, timeout=15)
    response.raise_for_status()
    return True


def send_to_notion(report_data: dict[str, Any]) -> bool:
    """실행 요약을 Notion DB에 새 페이지로 저장한다.

    기존 원본에 상세 DB 스키마와 Upsert 구현이 없으므로 안전한 최소 등록으로 구성한다.
    TC ID 기반 Upsert는 DB 속성 스키마가 확정된 후 별도 구현해야 한다.
    """
    notion_token = os.getenv("NOTION_API_KEY", "").strip()
    database_id = os.getenv("NOTION_DATABASE_ID", "").strip()

    if not notion_token or not database_id:
        print("[INFO] Notion 환경변수 미설정: Notion 전송 생략")
        return False

    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "TC-ID": {
                "title": [
                    {"text": {"content": f"QA Run {report_data['run_id']}"}}
                ]
            }
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": json.dumps(
                                    {
                                        "checkpoint4": report_data["checkpoint4"],
                                        "execution": report_data["execution"],
                                        "pytest_summary": report_data["pytest_summary"],
                                        "qa_classification_summary": report_data["qa_classification_summary"],
                                    },
                                    ensure_ascii=False,
                                )
                            },
                        }
                    ]
                },
            }
        ],
    }

    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }

    response = requests.post(
        "https://api.notion.com/v1/pages",
        headers=headers,
        json=payload,
        timeout=20,
    )
    response.raise_for_status()
    return True


def main() -> int:
    print("\n[Agent 4] 결과 분석 및 Checkpoint 4 검증 시작\n")

    try:
        report_data = parse_report()
        html_report = parse_html_report()
        validation = checkpoint4_validate(report_data, html_report)
        write_json(CHECKPOINT4_PATH, validation)

        summary = build_summary(report_data, validation)
        write_json(SUMMARY_PATH, summary)

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

        slack_sent = send_to_slack(format_slack_payload(summary))
        notion_sent = send_to_notion(summary)

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
