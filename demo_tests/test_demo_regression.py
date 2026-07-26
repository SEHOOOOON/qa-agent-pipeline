# -*- coding: utf-8 -*-
"""영상 녹화용 정상 회귀 스위트.

통합 분류 스위트의 의도적 Fail/Skip 시나리오는 제외하고,
실제 브라우저 제어 8건과 Agent Workflow Demo UI 4건을 검증한다.
"""

import sys
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"
sys.path.insert(0, str(TESTS_DIR))

import test_controller as controller  # noqa: E402


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1600, "height": 900},
    }


def open_simulator(page: Page) -> None:
    page.goto(controller.VIRTUAL_CONTROLLER_URL, wait_until="domcontentloaded")
    expect(page.locator("#device-card-1")).to_be_visible(timeout=5000)


def open_agent_tower(page: Page) -> None:
    open_simulator(page)
    page.click("#tab-qa")
    expect(page.locator("#agent-1-btn")).to_be_visible()


def test_demo_001_environment_ready(page: Page):
    """[DEMO-001] 16대 장치와 QA 컨트롤러 로드"""
    controller.test_tc_env_000_pre_environment_check(page)


def test_demo_002_heat_mode_control(page: Page):
    """[DEMO-002] HEAT 모드 적용과 내부 상태 동기화"""
    controller.test_tc_mode_001_heat_mode_and_temp_apply(page)


def test_demo_003_fan_temperature_lock(page: Page):
    """[DEMO-003] FAN 모드 온도 제어 비활성화"""
    controller.test_tc_mode_002_fan_mode_temp_disabled(page)


def test_demo_004_dry_to_cool_recovery(page: Page):
    """[DEMO-004] DRY에서 COOL 복귀 시 온도 제어 재활성화"""
    controller.test_tc_mode_003_dry_mode_then_cool_reactivation(page)


def test_demo_005_all_device_lock(page: Page):
    """[DEMO-005] 16대 LOCK 표시와 중앙/현장 관제점 제어 차단 검증"""
    controller.test_tc_lock_001_all_devices_full_inspection(page)


def test_demo_006_ch05_control_block(page: Page):
    """[DEMO-006] CH05 오류 장치 제어 차단"""
    controller.test_tc_err_001_ch05_fault_injection_control_block(page)


def test_demo_007_batch_heat_control(page: Page):
    """[DEMO-007] 3대 장치 HEAT 일괄 제어"""
    controller.test_tc_int_002_multi_select_batch_control(page)


def test_demo_008_temperature_upper_boundary(page: Page):
    """[DEMO-008] 냉방 설정온도 30°C 상한 방어"""
    controller.test_tc_temp_001_upper_limit_boundary(page)


def test_demo_009_agent1_requirement_input(page: Page):
    """[DEMO-009] Agent 1 요구사항 입력 UI"""
    open_agent_tower(page)
    page.click("#agent-1-btn")
    expect(page.locator("#agent1-req-modal")).to_have_class("agent-modal-backdrop show")
    page.fill("#req-jira-url", "HVAC-QA-2026")
    requirement = (
        "LOCK 상태가 설정된 장치는 운전/정지, 운전 모드, 설정온도, 풍량 등 "
        "다른 관제점 제어 명령을 실행해도 상태값이 변경되지 않아야 하며, "
        "제어 차단 결과가 UI와 QA 로그에 표시되어야 한다."
    )
    page.fill("#req-memo", requirement)
    expect(page.locator("#req-memo")).to_have_value(requirement)


def test_demo_010_agent2_tc_review(page: Page):
    """[DEMO-010] Agent 2 테스트케이스 심사 UI"""
    open_agent_tower(page)
    page.click("#agent-2-btn")
    expect(page.locator("#agent-tc-modal")).to_have_class("agent-modal-backdrop show")
    expect(page.locator("#agent-tc-modal")).to_contain_text("3-Tier 품질 기준")


def test_demo_011_agent3_runner(page: Page):
    """[DEMO-011] Agent 3 실행 Workflow Demo UI"""
    open_agent_tower(page)
    page.click("#agent-3-btn")
    expect(page.locator("#agent3-runner-modal")).to_have_class("agent-modal-backdrop show")
    expect(page.locator("#runner-start-btn")).to_be_visible()


def test_demo_012_agent4_reporting(page: Page):
    """[DEMO-012] Agent 4 결과 분석·보고 Demo UI"""
    open_agent_tower(page)
    page.click("#agent-4-btn")
    expect(page.locator("#agent4-cicd-modal")).to_have_class("agent-modal-backdrop show")
    expect(page.locator("#cicd-run-btn")).to_be_visible()
