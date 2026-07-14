import os
import subprocess

commits = [
    ('773e15a', 'feat: QA Agent 파이프라인 V1 포트폴리오 구조 및 산출물 최종 구축'),
    ('4da5279', 'chore: README 이전 버전 롤백 및 미사용 프로토타입 스크립트 삭제'),
    ('8aa8df6', 'docs: README 내 핵심 성과, 파이프라인 흐름도 및 저장소 구조 업데이트'),
    ('7d3268a', 'feat(docs): 반응형 포트폴리오 웹페이지(index.html) 구축 및 디자인 업데이트'),
    ('060f6d9', 'docs: README 상단에 포트폴리오, 시뮬레이터, 깃허브 링크 배지 3종 추가')
]

subprocess.run(['git', 'checkout', '-b', 'temp_rewrite', '726817d'], check=True)

for hash_val, new_msg in commits:
    subprocess.run(['git', 'cherry-pick', hash_val], check=True)
    subprocess.run(['git', 'commit', '--amend', '-m', new_msg], check=True)

subprocess.run(['git', 'checkout', 'main'], check=True)
subprocess.run(['git', 'reset', '--hard', 'temp_rewrite'], check=True)
subprocess.run(['git', 'branch', '-D', 'temp_rewrite'], check=True)
