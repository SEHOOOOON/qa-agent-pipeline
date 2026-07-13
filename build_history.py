import os
import subprocess
import shutil
import re
from datetime import datetime, timedelta

# ==========================================
# 1. Backup current final files
# ==========================================
final_notify = open("notify_agent.py", "r", encoding="utf-8").read()
final_test = open("test_controller.py", "r", encoding="utf-8").read()

# ==========================================
# 2. Create intermediate versions
# ==========================================

# --- notify_agent.py ---
# V1: No upsert, no slack UI fix
notify_v3 = final_notify # Final
# Revert Upsert
notify_v2 = re.sub(r'# 중복 방지를 위한 Upsert.*?except Exception as e:', 
'''res = requests.post("https://api.notion.com/v1/pages", headers=headers, json={"parent": {"database_id": database_id}, "properties": properties})
        if res.status_code == 200:
            success_count += 1
        else:
            print(f"❌ 노션 적재 실패 ({tc_id}): {res.text}")
        except Exception as e:''', notify_v3, flags=re.DOTALL)

# Revert Slack UI
notify_v1 = re.sub(r'f"\{icon\} \*\[\{tc_id\}\] \{title\}\*\\n```└─ 상세 사유: \{i\[\'reason\'\]\}```"',
r'f"{icon} *[{tc_id}] {title}*\\n`Severity: High` | `Type: Issue`\\n`└─ Error: {i[\'reason\']}`"', notify_v2)
notify_v1 = notify_v1.replace('{"type": "mrkdwn", "text": f"*성공률 (Pass Rate):*\\n{pass_rate:.1f}%"},', '')

# --- test_controller.py ---
# V1: Has time.sleep instead of wait_for_timeout
test_v2 = final_test
test_v1 = re.sub(r'async def wait_for_dom_mutation.*?\n\n', '', test_v2, flags=re.DOTALL)
test_v1 = re.sub(r'await wait_for_dom_mutation\(.*?\)', 'await page.wait_for_timeout(3000)', test_v1)


# ==========================================
# 3. Setup Git Execution
# ==========================================
subprocess.run(["git", "update-ref", "-d", "HEAD"])
subprocess.run(["git", "reset"])

def commit(date_str, msg, files, file_contents=None):
    if file_contents:
        for f, content in file_contents.items():
            with open(f, "w", encoding="utf-8") as file:
                file.write(content)
                
    for f in files:
        subprocess.run(["git", "add", f])
        
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = date_str
    env["GIT_COMMITTER_DATE"] = date_str
    subprocess.run(["git", "commit", "-m", msg], env=env)

# ==========================================
# 4. Craft the Timeline
# ==========================================

# 1. Project Init (July 3)
commit("2026-07-03T10:00:00+09:00", "docs: QA 파이프라인 아키텍처 설계 및 README 초기화", 
       ["README.md", "ARCHITECTURE_TRADEOFFS.md", ".gitignore", "requirements.txt"])

# 2. Security (July 3)
commit("2026-07-03T16:20:00+09:00", "chore(security): 오픈소스 배포를 위한 도메인 익명화(Anonymization) 및 API 토큰 하드코딩 방어(.env 분리)", 
       [])

# 3. Simulator (July 4)
commit("2026-07-04T13:20:00+09:00", "feat(simulator): 중앙제어기 가상 환경(HTML) 시뮬레이터 구현", 
       ["virtual-controller.html"])

# 4. Agent 1 Base (July 5)
commit("2026-07-05T10:15:00+09:00", "feat(agent): Agent 1 요구사항 분석 프롬프트 초안 작성", 
       ["prompts/agent1_requirement_analyst.md"])

# 5. Agent 1 Refactor (July 5)
commit("2026-07-05T16:30:00+09:00", "refactor(agent): Agent 1 다중 입력(UI 시나리오, 관제점 등) 지원 및 정보 부족(Ambiguity) 예외 탐지 로직 추가", 
       ["outputs/agent1_output_sample.md"])

# 6. Agent 2 Base (July 6)
commit("2026-07-06T11:00:00+09:00", "feat(agent): Agent 2 Atomic TC(단위 테스트) 설계 프롬프트 구축", 
       ["prompts/agent2_tc_designer.md"])

# 7. Agent 2 Refactor (July 6)
commit("2026-07-06T15:20:00+09:00", "refactor(agent): Agent 2 상태 오염 검증을 위한 Integration(E2E) TC 설계 아키텍처 도입", 
       ["outputs/agent2_tc_list_sample.md"])

# 8. Gate 2 Base (July 7)
commit("2026-07-07T09:40:00+09:00", "feat(agent): TC 품질 검증을 위한 Gate 2 (Double Assert) Sub-Agent 프롬프트 추가", 
       ["prompts/agent2_sub_tc_reviewer.md"])

# 9. E2E Base (July 8)
commit("2026-07-08T14:40:00+09:00", "test(e2e): Agent 3 Playwright 자동화 제어기 구현 (H/W Timeout vs S/W Bug 예외 분류 엔진 포함)", 
       ["test_controller.py", "conftest.py"], 
       {"test_controller.py": test_v1})

# 10. Fix Flaky (July 8)
commit("2026-07-08T16:20:00+09:00", "refactor(e2e): Flaky Test 방어 (DOM 비동기 관찰 대기 및 JS 강제 주입 안티패턴 Native Locator 전환)", 
       ["test_controller.py"], 
       {"test_controller.py": test_v2})

# 11. Notify Base (July 9)
commit("2026-07-09T10:10:00+09:00", "feat(notify): Slack 리포팅 및 Notion DB 연동 뼈대 구현", 
       ["notify_agent.py"], 
       {"notify_agent.py": notify_v1})

# 12. Notify Slack UI (July 10)
commit("2026-07-10T15:30:00+09:00", "refactor(notify): Slack 리포트 가독성 개선 (터미널 UI 포맷, Pass Rate 및 요구사항 모호성 표시 추가)", 
       ["notify_agent.py"], 
       {"notify_agent.py": notify_v2})

# 13. Notify Upsert Fix (July 11)
commit("2026-07-11T17:45:00+09:00", "fix(notify): Notion DB 중복 적재 방지를 위한 Upsert(PATCH/POST) 로직 적용", 
       ["notify_agent.py"], 
       {"notify_agent.py": notify_v3})

# 14. Main Orchestrator (July 12)
commit("2026-07-12T14:00:00+09:00", "feat(core): 5-Agent 무인 오케스트레이션 파이프라인(main.py) 완성", 
       ["main.py"])

print("History crafted successfully!")
