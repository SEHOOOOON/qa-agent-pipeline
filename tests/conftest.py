# conftest.py
# pytest-html v4 compatible configuration for 가상 관제 시스템 QA Test Suite
# ※ Screenshot·Trace·상태 Snapshot 수집 기능은 향후 고도화 대상으로 관리합니다.

import pytest
import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from test_controller import SimulatorTimeoutError

# 프로젝트 루트 기준 reports 경로 (tests/ 폴더 한 단계 위)
REPORTS_DIR = Path(__file__).parent.parent / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
QA_RESULTS_PATH = REPORTS_DIR / "qa_results.json"

# Global test results collector
qa_results = []
session_run_id = str(uuid.uuid4())
session_start_time = datetime.now()

# -- 1. Viewport fixture -------------------------------------------------------
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """가상 관제 시스템 dashboard 4-column grid optimal viewport (1600x900)."""
    return {
        **browser_context_args,
        "viewport": {"width": 1600, "height": 900},
    }

# -- 2. Extract docstring & Classify Failure -> report attributes ----------------
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call":
        # Description
        doc = getattr(item.function, "__doc__", "") or ""
        first_line = next((line.strip() for line in doc.splitlines() if line.strip()), "")
        report.description = first_line
        
        # Failure Classification
        report.failure_reason = ""
        if report.outcome == "skipped":
            if "기획" in str(report.longrepr) or "요구사항" in str(report.longrepr):
                report.failure_reason = "2. 기획·요구사항 확인 필요"
            else:
                report.failure_reason = "5. 조건 부족으로 미실행"
        elif report.failed and call.excinfo:
            exc_type = call.excinfo.type
            if exc_type.__name__ == 'SimulatorTimeoutError':
                report.failure_reason = "3. 테스트 환경·시뮬레이터 문제"
            elif exc_type is AssertionError:
                report.failure_reason = "1. 제품 결함 후보"
            else:
                report.failure_reason = "4. 자동화 코드 문제"

        # Extract TC ID
        tc_match = re.search(r'\[(.*?)\]', report.description)
        tc_id = tc_match.group(1) if tc_match else "UNKNOWN_TC"
        
        # Save to global array for JSON export
        qa_results.append({
            "run_id": session_run_id,
            "tc_id": tc_id,
            "test_id": item.name,
            "description": report.description,
            "result": report.outcome,
            "failure_reason": report.failure_reason,
            "executed_at": datetime.now().isoformat(),
            "duration": round(report.duration, 2),
            "evidence_path": ""
        })

def pytest_sessionfinish(session, exitstatus):
    with open(QA_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(qa_results, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] QA 결과 저장 완료: {QA_RESULTS_PATH}")

# -- 2.5 Fix pytest-html Summary Count Bug --------------------------------------
def pytest_html_results_summary(prefix, summary, postfix):
    """
    pytest-html의 기본 summary는 skipped/failed 처리 시점에 따라 실제 수집된 테스트 수와 
    달라지는 버그가 있습니다. 이를 json에 수집된 정확한 qa_results 배열 길이로 덮어씌웁니다.
    """
    total_tests = len(qa_results)
    duration = round((datetime.now() - session_start_time).total_seconds(), 2)
    # 기존 summary 요소 중 run-count p 태그를 찾아서 교체
    for i, element in enumerate(summary):
        if hasattr(element, "tag") and element.tag == "p" and "run-count" in getattr(element, "attributes", {}).get("class", ""):
            summary[i] = f'<p class="run-count">{total_tests} tests took {duration} seconds.</p>'
            break

# -- 3. Add Columns headers -----------------------------------------
def pytest_html_results_table_header(cells):
    cells.insert(2, '<th class="sortable" data-column-type="description">Description</th>')
    cells.insert(3, '<th class="sortable" data-column-type="failure_reason">Failure Classification</th>')

# -- 4. Add Columns cell per row ------------------------------------
def pytest_html_results_table_row(report, cells):
    description = getattr(report, "description", "")
    failure_reason = getattr(report, "failure_reason", "")
    
    # 실패 분류에 따른 색상 스타일링
    color_style = ""
    if "1. 제품 결함 후보" in failure_reason:
        color_style = "color: #f85149; font-weight: bold;" # Red
    elif "2. 기획" in failure_reason:
        color_style = "color: #db6d28; font-weight: bold;" # Orange
    elif "3. 테스트 환경" in failure_reason or "4. 자동화 코드" in failure_reason:
        color_style = "color: #d29922; font-weight: bold;" # Yellow
    elif "5. 조건 부족" in failure_reason:
        color_style = "color: #8b949e; font-style: italic;" # Gray
    
    cells.insert(2, f'<td class="col-description">{description}</td>')
    cells.insert(3, f'<td class="col-failure-reason" style="{color_style}">{failure_reason}</td>')

# -- 5. Report title -----------------------------------------------------------
def pytest_html_report_title(report):
    report.title = "Virtual Central Control System — QA Automation Report"
