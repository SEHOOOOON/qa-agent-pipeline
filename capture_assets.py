import asyncio
from playwright.async_api import async_playwright
import os

async def capture_assets():
    os.makedirs("assets", exist_ok=True)
    html_path = f"file:///{os.path.abspath('virtual-controller.html').replace(chr(92), '/')}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1400, "height": 900}, record_video_dir="assets/")
        page = await context.new_page()
        
        print("페이지 로딩 중...")
        await page.goto(html_path)
        await page.wait_for_timeout(2000) # 초기 렌더링 대기
        
        print("1. 시뮬레이터 대기 상태 캡처")
        await page.screenshot(path="assets/simulator_ready.png", full_page=True)
        
        print("2. Master QA 시퀀스 가동")
        await page.evaluate("document.getElementById('agent-lead-btn').click()")
        await page.wait_for_timeout(2500) # Agent 2 실행 중
        
        print("3. 파이프라인 중간 흐름 캡처")
        await page.screenshot(path="assets/simulator_agent_flow.png", full_page=True)
        
        await page.wait_for_timeout(4000) # 파이프라인 완료 대기
        
        print("4. 파이프라인 완료 상태 캡처")
        await page.screenshot(path="assets/simulator_complete.png", full_page=True)
        
        # 특정 영역 캡처 (로그 패널)
        print("5. 로그 패널 캡처")
        log_panel = await page.query_selector(".qa-logger")
        if log_panel:
            await log_panel.screenshot(path="assets/simulator_logs.png")
            
        await browser.close()
        print("모든 스크린샷 캡처 완료!")

if __name__ == "__main__":
    asyncio.run(capture_assets())
