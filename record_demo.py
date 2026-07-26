# -*- coding: utf-8 -*-
"""가상 관제 QA 포트폴리오 구현 영상 자동 생성.

1. Agent 1~4 Workflow Demo와 실제 Playwright 장치 제어를 브라우저 영상으로 녹화
2. 영상 전용 정상 회귀 12건을 실제 실행
3. 실제 Pytest stdout을 터미널 스타일 영상으로 녹화
4. Notion TC 테이블과 Slack 최신 알림 캡처를 마지막 장면으로 추가
5. 전체 영상을 H.264 MP4로 연결해 assets/playwright_pipeline_demo.mp4 생성
"""

from __future__ import annotations

import html
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import Page, sync_playwright


PROJECT_ROOT = Path(__file__).resolve().parent
SIMULATOR_URL = (PROJECT_ROOT / "virtual-controller.html").as_uri()
OUTPUT_PATH = PROJECT_ROOT / "assets" / "playwright_pipeline_demo.mp4"
NOTION_CAPTURE_PATH = PROJECT_ROOT / "assets" / "notion_tc_table.png"
SLACK_CAPTURE_PATH = PROJECT_ROOT / "assets" / "slack_latest_alarm.png"
VIEWPORT = {"width": 1600, "height": 900}


def add_recording_overlay(page: Page) -> None:
    page.evaluate(
        """() => {
            if (document.getElementById('recording-overlay')) return;
            const style = document.createElement('style');
            style.textContent = `
                #recording-overlay {
                    position: fixed; left: 26px; top: 22px; z-index: 999999;
                    padding: 10px 16px; border-radius: 999px;
                    color: #fff; background: rgba(8,12,19,.88);
                    border: 1px solid rgba(88,166,255,.65);
                    box-shadow: 0 8px 28px rgba(0,0,0,.4);
                    font: 700 13px/1.2 Arial, sans-serif;
                    letter-spacing: .04em; backdrop-filter: blur(8px);
                }
                .record-click-pulse {
                    position: fixed; width: 34px; height: 34px; margin: -17px 0 0 -17px;
                    z-index: 999998; pointer-events: none; border-radius: 50%;
                    border: 3px solid #58a6ff; background: rgba(88,166,255,.2);
                    animation: recordPulse .55s ease-out forwards;
                }
                @keyframes recordPulse {
                    from { transform: scale(.35); opacity: 1; }
                    to { transform: scale(1.8); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
            const badge = document.createElement('div');
            badge.id = 'recording-overlay';
            badge.textContent = 'QA WORKFLOW DEMO';
            document.body.appendChild(badge);
            document.addEventListener('click', event => {
                const pulse = document.createElement('div');
                pulse.className = 'record-click-pulse';
                pulse.style.left = `${event.clientX}px`;
                pulse.style.top = `${event.clientY}px`;
                document.body.appendChild(pulse);
                setTimeout(() => pulse.remove(), 650);
            }, true);
        }"""
    )


def set_overlay(page: Page, text: str) -> None:
    page.evaluate(
        "(text) => { document.getElementById('recording-overlay').textContent = text; }",
        text,
    )


def pause(page: Page, milliseconds: int = 1000) -> None:
    page.wait_for_timeout(milliseconds)


def record_browser_workflow(playwright, recording_dir: Path) -> Path:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        viewport=VIEWPORT,
        record_video_dir=str(recording_dir),
        record_video_size=VIEWPORT,
        color_scheme="dark",
    )
    page = context.new_page()
    page.goto(SIMULATOR_URL, wait_until="domcontentloaded")
    page.wait_for_selector("#device-card-1", timeout=5000)
    add_recording_overlay(page)
    pause(page, 1400)

    # Agent 1: 실제 입력 동작 + Workflow Demo
    page.click("#tab-qa")
    set_overlay(page, "WORKFLOW DEMO · AGENT 1 REQUIREMENT")
    page.click("#agent-1-btn")
    page.wait_for_selector("#agent1-req-modal.show")
    page.fill("#req-jira-url", "HVAC-QA-2026")
    page.fill(
        "#req-memo",
        "LOCK 상태가 설정된 장치는 운전/정지, 운전 모드, 설정온도, 풍량 등 "
        "다른 관제점 제어 명령을 실행해도 상태값이 변경되지 않아야 하며, "
        "제어 차단 결과가 UI와 QA 로그에 표시되어야 한다.",
    )
    pause(page, 1200)
    page.click("button:has-text('요구사항 분석 및 TC 생성 시작')")
    page.wait_for_selector("#simulation-final-confirm", state="visible", timeout=10000)
    pause(page, 1200)
    page.click("#simulation-final-confirm")
    pause(page, 900)

    # Agent 2: 품질 기준 매트릭스 확인
    set_overlay(page, "WORKFLOW DEMO · AGENT 2 TC REVIEW")
    page.click("#agent-2-btn")
    page.wait_for_selector("#agent-tc-modal.show")
    pause(page, 1800)
    page.locator("#agent-tc-modal .agent-modal-close").click()
    pause(page, 700)

    # Agent 3: 13건 분류 파이프라인 Workflow Demo
    set_overlay(page, "WORKFLOW DEMO · AGENT 3 PIPELINE")
    page.click("#agent-3-btn")
    page.wait_for_selector("#agent3-runner-modal.show")
    page.click("#runner-start-btn")
    page.wait_for_function(
        "() => document.getElementById('runner-title').textContent.includes('완료')",
        timeout=10000,
    )
    pause(page, 1800)
    page.locator("#agent3-runner-modal .agent-modal-close").click()
    pause(page, 700)

    # Agent 4: 실제 결과 구조를 반영한 분류·보고 Workflow Demo
    set_overlay(page, "WORKFLOW DEMO · AGENT 4 REPORTING")
    page.click("#agent-4-btn")
    page.wait_for_selector("#agent4-cicd-modal.show")
    page.click("#cicd-run-btn")
    page.wait_for_selector("#cicd-jira-area", state="visible", timeout=12000)
    pause(page, 1800)
    page.locator("#agent4-cicd-modal .agent-modal-close").click()
    pause(page, 900)

    # 실제 Playwright LOCK 설정 및 다른 중앙 관제점 제어 차단
    set_overlay(page, "REAL PLAYWRIGHT CONTROL · LOCK ON")
    page.click("#tab-control")
    page.click("#device-card-1 .card-body-split")
    page.wait_for_function(
        "() => document.getElementById('det-unit-name').textContent.includes('IDU-00')"
    )
    page.click("#det-lock-on-btn")
    page.click(".btn-apply-cmd")
    page.wait_for_function("() => window.__vccs.devices[0].locked === true")
    pause(page, 900)

    set_overlay(page, "LOCKED DEVICE · OTHER CONTROL POINTS BLOCKED")
    page.click("#det-mode-heat")
    page.click("#det-fan-high")
    pause(page, 800)
    page.click(".btn-apply-cmd")
    pause(page, 900)
    page.click("#tab-test-panel")
    page.wait_for_selector("#qa-drawer-panel.open")
    page.wait_for_function(
        """() => Array.from(document.querySelectorAll('.qa-log-text'))
            .some(el => el.textContent.includes('LOCK 상태로'))""",
        timeout=4000,
    )
    set_overlay(page, "REAL EVIDENCE · STATE UNCHANGED + BLOCK LOG")
    pause(page, 2600)

    video = page.video
    context.close()
    video_path = Path(video.path())
    browser.close()
    return video_path


def run_demo_regression() -> str:
    command = [
        sys.executable,
        "-m",
        "pytest",
        r"demo_tests\test_demo_regression.py",
        "-q",
        "--browser",
        "chromium",
        "-o",
        "addopts=",
    ]
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
        timeout=120,
        check=False,
    )
    output = (completed.stdout + "\n" + completed.stderr).strip()
    if completed.returncode != 0 or "12 passed" not in output:
        raise RuntimeError(f"영상용 정상 회귀 실패\n{output}")
    return output


def create_terminal_html(path: Path, pytest_output: str) -> None:
    safe_output = html.escape(pytest_output)
    document = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<style>
*{{box-sizing:border-box}} html,body{{margin:0;width:100%;height:100%;overflow:hidden}}
body{{background:radial-gradient(circle at 20% 0%,#12233d,#05070c 62%);
color:#dce6f3;font-family:Consolas,'Courier New',monospace;padding:58px}}
.caption{{color:#58a6ff;font:700 14px Arial,sans-serif;letter-spacing:.12em;margin-bottom:18px}}
.terminal{{height:760px;background:rgba(6,10,16,.96);border:1px solid #2a3c55;border-radius:16px;
box-shadow:0 30px 70px rgba(0,0,0,.55);overflow:hidden}}
.bar{{height:48px;background:#111927;border-bottom:1px solid #26364b;display:flex;align-items:center;
padding:0 18px;color:#9fb0c5;font:600 13px Arial,sans-serif}}
.dots{{display:flex;gap:8px;margin-right:18px}} .dot{{width:11px;height:11px;border-radius:50%}}
.red{{background:#ff5f57}} .yellow{{background:#febc2e}} .green{{background:#28c840}}
.screen{{padding:28px 32px;font-size:18px;line-height:1.72;white-space:pre-wrap}}
.prompt{{color:#58a6ff}} .command{{color:#f0f6fc}} .output{{opacity:0;animation:show 1s ease .8s forwards}}
.success{{color:#3fb950;font-weight:800;font-size:26px;margin-top:18px;opacity:0;animation:show .8s ease 3.8s forwards}}
.note{{color:#8b949e;font-size:15px;margin-top:18px;opacity:0;animation:show .8s ease 4.6s forwards}}
@keyframes show{{to{{opacity:1}}}}
</style>
</head>
<body>
<div class="caption">REAL PYTEST EXECUTION · VIDEO REGRESSION SUITE</div>
<div class="terminal">
  <div class="bar"><div class="dots"><i class="dot red"></i><i class="dot yellow"></i><i class="dot green"></i></div>PowerShell — QA Automation</div>
  <div class="screen"><span class="prompt">PS portfolio_export&gt; </span><span class="command">python -m pytest demo_tests\\test_demo_regression.py -q --browser chromium -o "addopts="</span>

<span class="output">{safe_output}</span>
<div class="success">✓ 12 PASSED · NORMAL REGRESSION COMPLETE</div>
<div class="note">통합 분류 스위트(13건)와 분리된 영상용 정상 회귀 실행입니다.</div></div>
</div>
</body></html>"""
    path.write_text(document, encoding="utf-8")


def record_terminal(playwright, terminal_html: Path, recording_dir: Path) -> Path:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        viewport=VIEWPORT,
        record_video_dir=str(recording_dir),
        record_video_size=VIEWPORT,
        color_scheme="dark",
    )
    page = context.new_page()
    page.goto(terminal_html.as_uri(), wait_until="load")
    page.wait_for_timeout(8000)
    video = page.video
    context.close()
    video_path = Path(video.path())
    browser.close()
    return video_path


def find_ffmpeg() -> str:
    executable = shutil.which("ffmpeg")
    if executable:
        return executable

    temporary_dependency = Path(r"C:\tmp\qa-video-deps")
    if temporary_dependency.exists():
        sys.path.insert(0, str(temporary_dependency))
    try:
        import imageio_ffmpeg
    except ImportError as exc:
        raise RuntimeError(
            "ffmpeg가 필요합니다: python -m pip install imageio-ffmpeg"
        ) from exc
    return imageio_ffmpeg.get_ffmpeg_exe()


def combine_to_mp4(
    ffmpeg: str,
    browser_video: Path,
    terminal_video: Path,
    notion_capture: Path,
    slack_capture: Path,
) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    for capture in (notion_capture, slack_capture):
        if not capture.exists():
            raise FileNotFoundError(f"외부 보고 캡처를 찾을 수 없습니다: {capture}")

    command = [
        ffmpeg,
        "-y",
        "-i",
        str(browser_video),
        "-i",
        str(terminal_video),
        "-loop",
        "1",
        "-framerate",
        "30",
        "-t",
        "3",
        "-i",
        str(notion_capture),
        "-loop",
        "1",
        "-framerate",
        "30",
        "-t",
        "3",
        "-i",
        str(slack_capture),
        "-filter_complex",
        (
            "[0:v]fps=30,scale=1600:900,setsar=1,format=yuv420p,settb=1/30,setpts=N[v0];"
            "[1:v]fps=30,scale=1600:900,setsar=1,format=yuv420p,settb=1/30,setpts=N[v1];"
            "[2:v]scale=1600:900:force_original_aspect_ratio=decrease,"
            "pad=1600:900:(ow-iw)/2:(oh-ih)/2:color=0x0d1117,"
            "setsar=1,fps=30,format=yuv420p,settb=1/30,setpts=N[v2];"
            "[3:v]scale=1600:900:force_original_aspect_ratio=decrease,"
            "pad=1600:900:(ow-iw)/2:(oh-ih)/2:color=0x0d1117,"
            "setsar=1,fps=30,format=yuv420p,settb=1/30,setpts=N[v3];"
            "[v0][v1][v2][v3]concat=n=4:v=1:a=0[v]"
        ),
        "-map",
        "[v]",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "23",
        "-movflags",
        "+faststart",
        str(OUTPUT_PATH),
    ]
    subprocess.run(command, check=True, timeout=240)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="qa-portfolio-video-") as temporary:
        work_dir = Path(temporary)
        browser_recordings = work_dir / "browser"
        terminal_recordings = work_dir / "terminal"
        browser_recordings.mkdir()
        terminal_recordings.mkdir()

        with sync_playwright() as playwright:
            print("[1/4] Agent Workflow + 실제 관제 제어 녹화")
            browser_video = record_browser_workflow(playwright, browser_recordings)

            print("[2/4] 영상용 정상 회귀 12건 실제 실행")
            pytest_output = run_demo_regression()
            print(pytest_output)

            print("[3/4] 실제 Pytest 출력 터미널 화면 녹화")
            terminal_html = work_dir / "pytest-terminal.html"
            create_terminal_html(terminal_html, pytest_output)
            terminal_video = record_terminal(
                playwright,
                terminal_html,
                terminal_recordings,
            )

        print("[4/4] H.264 MP4 연결 및 최적화")
        combine_to_mp4(
            find_ffmpeg(),
            browser_video,
            terminal_video,
            NOTION_CAPTURE_PATH,
            SLACK_CAPTURE_PATH,
        )

    print(f"[DONE] {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
