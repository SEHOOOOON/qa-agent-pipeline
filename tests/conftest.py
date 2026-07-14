# conftest.py
# pytest-html v4 compatible configuration for 가상 관제 시스템 QA Test Suite

import pytest
import json
from pathlib import Path
from test_controller import SimulatorTimeoutError

# 프로젝트 루트 기준 reports 경로 (tests/ 폴더 한 단계 위)
REPORTS_DIR = Path(__file__).parent.parent / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
QA_RESULTS_PATH = REPORTS_DIR / "qa_results.json"

# Global test results collector
qa_results = []

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

        # Save to global array for JSON export
        qa_results.append({
            "test_id": item.name,
            "description": report.description,
            "result": report.outcome,
            "failure_reason": report.failure_reason
        })

def pytest_sessionfinish(session, exitstatus):
    with open(QA_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(qa_results, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] QA 결과 저장 완료: {QA_RESULTS_PATH}")

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
