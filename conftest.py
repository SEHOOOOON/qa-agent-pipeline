# conftest.py
# pytest-html v4 compatible configuration for 가상 관제 시스템 QA Test Suite

import pytest
import json
from test_controller import RequirementAmbiguityError, HardwareIssueError

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
        if report.failed and call.excinfo:
            exc_type = call.excinfo.type
            if exc_type.__name__ == 'RequirementAmbiguityError':
                report.failure_reason = "⚠️ 요구사항 확인 필요 (Requirement Ambiguity)"
            elif exc_type.__name__ == 'HardwareIssueError':
                report.failure_reason = "🔌 H/W 장비 점검 (Hardware Issue)"
            elif exc_type is AssertionError:
                report.failure_reason = "🐛 제품 결함 확보 (Product Defect)"
            elif "TimeoutError" in exc_type.__name__:
                report.failure_reason = "⚠️ 환경/스크립트 오류 (Timeout/Env)"
            else:
                report.failure_reason = "❓ 미기입 에러 (Unknown Error)"

        # Save to global array for JSON export
        qa_results.append({
            "test_id": item.name,
            "description": report.description,
            "result": report.outcome,
            "failure_reason": report.failure_reason
        })

def pytest_sessionfinish(session, exitstatus):
    with open("qa_results.json", "w", encoding="utf-8") as f:
        json.dump(qa_results, f, ensure_ascii=False, indent=2)

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
    if "요구사항" in failure_reason:
        color_style = "color: #db6d28; font-weight: bold;" # Orange
    elif "제품 결함" in failure_reason:
        color_style = "color: #f85149; font-weight: bold;" # Red
    elif "스크립트" in failure_reason:
        color_style = "color: #d29922; font-weight: bold;" # Yellow
    
    cells.insert(2, f'<td class="col-description">{description}</td>')
    cells.insert(3, f'<td class="col-failure-reason" style="{color_style}">{failure_reason}</td>')

# -- 5. Report title -----------------------------------------------------------
def pytest_html_report_title(report):
    report.title = "가상 가상 관제 시스템 Virtual Control System - QA Automation Report"
