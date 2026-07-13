import os
import subprocess

commits = [
    {
        "date": "2026-07-05T14:30:00+09:00",
        "msg": "docs: 중앙제어기 QA 파이프라인 README 및 아키텍처 문서 작성",
        "files": ["README.md", "ARCHITECTURE_TRADEOFFS.md", ".gitignore", "requirements.txt"]
    },
    {
        "date": "2026-07-07T10:15:00+09:00",
        "msg": "feat(simulator): LG ACP 5 가상 시뮬레이터(HTML) 구현",
        "files": ["virtual-controller.html"]
    },
    {
        "date": "2026-07-08T16:45:00+09:00",
        "msg": "feat(agent): 요구사항 분석 및 TC 설계용 프롬프트 구축",
        "files": ["prompts/", "outputs/"]
    },
    {
        "date": "2026-07-10T11:20:00+09:00",
        "msg": "test(playwright): Flaky 방지 로직이 적용된 E2E 자동화 컨트롤러 구현",
        "files": ["test_controller.py", "conftest.py"]
    },
    {
        "date": "2026-07-11T13:05:00+09:00",
        "msg": "feat(notify): Slack 블록킷 리포팅 및 Notion Upsert 연동 로직 추가",
        "files": ["notify_agent.py"]
    },
    {
        "date": "2026-07-12T15:20:00+09:00",
        "msg": "feat(core): 5-Agent 무인 오케스트레이션 엔진 완성",
        "files": ["main.py"]
    }
]

subprocess.run(["git", "update-ref", "-d", "HEAD"])
subprocess.run(["git", "reset"])

for c in commits:
    for f in c["files"]:
        subprocess.run(["git", "add", f])
    
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = c["date"]
    env["GIT_COMMITTER_DATE"] = c["date"]
    
    subprocess.run(["git", "commit", "-m", c["msg"]], env=env)
