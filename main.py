import os
import sys
import time
import subprocess
from pathlib import Path

# =============================================================================
# main.py
# 가??중앙?어?QA 5-Agent ?이?라?????트?이??(Orchestrator)
# =============================================================================
# ???크립트??5개의 Agent가 ?기?으??결??E2E QA ?이?라?을 구동?니??
# 
# [Agent 1] ?구?항 분석 ?리스???별 (Requirement Refiner)
# [Agent 2] E2E ?제??TC ?계 (TC Architect)
# [Gate  2] ?브 ?이?트 TC ?질 리뷰 ??각 ?제 (Quality Reviewer)
# [Agent 3] Playwright ?동???스???행 (Execution Robot)
# [Agent 4] Slack 리포????사결정 추천 (Report Manager)
# =============================================================================

sys.stdout.reconfigure(encoding='utf-8')
BASE_DIR = Path(__file__).parent

def print_header(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def simulate_llm_processing(agent_name, duration=2):
    print(f"[{agent_name}] LLM 추론 ?(Generating...)", end="")
    for _ in range(duration):
        time.sleep(0.5)
        print(".", end="", flush=True)
    print(" ?료!\n")

def run_agent1_and_2():
    print_header("? Agent 1 & Agent 2: ?구?항 분석 ?TC ?계")
    print("1. ?롬?트 로드 ? prompts/agent1_requirement_analyst.md")
    time.sleep(1)
    simulate_llm_processing("Agent 1")
    print(">> [Agent 1] ?러 관?점 ?시 ?어 ???태 ?염(E2E ?합???손) 리스?? ?별?습?다.")
    print(">> [Agent 1] 분석 보고?? Agent 2??달?니??\n")
    
    print("2. ?롬?트 로드 ? prompts/agent2_tc_designer.md")
    time.sleep(1)
    simulate_llm_processing("Agent 2")
    print(">> [Agent 2] Agent 1??리스??보고?? 바탕?로 TC??계?습?다.")
    print(">> [Agent 2] 관?점?'Atomic TC' 7? ?체 ?시 ?어 'Integration TC' 3??성 ?료.\n")
    
    print("3. ?롬?트 로드 ? prompts/agent2_sub_tc_reviewer.md")
    time.sleep(1)
    simulate_llm_processing("Gate 2 (Sub-Agent)")
    print(">> [Gate 2] ?각 ?제 ?스?? 모든 TC가 8? ?질 기? ?Double-Assert?준?함???인?습?다.")
    print(">> [Gate 2] 최종 ?인. 결과?outputs/ ?렉?리????합?다.\n")

def run_agent3(headed=False):
    print_header("? Agent 3: Playwright ?동???행 ?진")
    print(">> [Agent 3] TC-00 ?전 ?경 검??test_controller.py ?행???작?니??..")
    
    # pytest 명령??구성
    cmd = ["pytest", "test_controller.py", "-v", "--html=report.html"]
    if headed:
        cmd.extend(["--headed", "--slowmo", "500"])
        
    try:
        subprocess.run(cmd, cwd=BASE_DIR, check=False)
    except Exception as e:
        print(f"Agent 3 ?행 ??러 발생: {e}")

def run_agent4():
    print_header("? Agent 4: ?랙 리포??매니? (?사결정 추천)")
    print(">> [Agent 4] Agent 3가 ?긴 qa_results.json 결과?분석?니??..")
    
    notify_script = BASE_DIR / "notify_agent.py"
    if not notify_script.exists():
        print("??notify_agent.py ?일??찾을 ???습?다.")
        return
        
    try:
        subprocess.run([sys.executable, str(notify_script)], cwd=BASE_DIR, check=False)
    except Exception as e:
        print(f"Agent 4 ?행 ??러 발생: {e}")

def main_menu():
    while True:
        print("\n\n" + "="*60)
        print(" ?? [ 중앙?어?QA 5-Agent Pipeline Orchestrator ]")
        print("="*60)
        print(" [1] ?체 ?이?라???동 ?행 (Agent 1 ??2 ??3 ??4)")
        print(" [2] ?단(Agent 1, 2) 추론 ???이???독 ?행")
        print(" [3] ?스???행(Agent 3) ?독 ?행 (Headless)")
        print(" [4] ?스???각 ?행(Agent 3) ?독 ?행 (브라?? ?출)")
        print(" [5] ?랙 리포??Agent 4) ?독 ?행")
        print(" [0] ?로그램 종료")
        print("="*60)
        
        choice = input("?행??메뉴??번호??력?세?? ").strip()
        
        if choice == '1':
            run_agent1_and_2()
            run_agent3(headed=False)
            run_agent4()
        elif choice == '2':
            run_agent1_and_2()
        elif choice == '3':
            run_agent3(headed=False)
        elif choice == '4':
            run_agent3(headed=True)
        elif choice == '5':
            run_agent4()
        elif choice == '0':
            print("?로그램??종료?니??")
            break
        else:
            print("?못???력?니?? 0~5 ?이???자??력?주?요.")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n?로그램??강제 종료?니??")
        sys.exit(0)
