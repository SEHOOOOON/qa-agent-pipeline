<div align="center">

<!-- 2026-10-09: 야간 검토 브랜치 안내. V1 실행 코드·기준 자산은 수정하지 않음. -->

<h1>QA 판단 기준 기반 Multi-Agent Workflow</h1>

<p>요구사항 정제부터 테스트 설계, Playwright 실행, 비통과 원인 분류와 보고까지<br/>QA 변경 검증 흐름을 4개의 Agent와 4개의 Checkpoint로 구조화한 개인 프로젝트입니다.</p>

[![포트폴리오 홈](https://img.shields.io/badge/Portfolio-Home-58A6FF?style=for-the-badge&labelColor=0b1220)](https://SEHOOOOON.github.io/qa-agent-pipeline/)
[![프로젝트 상세](https://img.shields.io/badge/Project-Detail-58A6FF?style=for-the-badge&labelColor=0b1220)](https://SEHOOOOON.github.io/qa-agent-pipeline/project.html)
[![가상 관제 화면](https://img.shields.io/badge/Live-Simulator-58A6FF?style=for-the-badge&labelColor=0b1220)](https://SEHOOOOON.github.io/qa-agent-pipeline/virtual-controller.html)

</div>

---

> AI가 만든 산출물을 그대로 신뢰하지 않습니다.<br/>
> 각 단계의 입력·출력과 판단 근거를 QA Checkpoint에서 검토한 뒤 다음 단계로 전달합니다.

## 프로젝트 한눈에 보기

> **야간 검토본 안내 (2026-10-09)**: `codex/night-review-20261009`의 `index.html`은 최신 메인 소개 페이지입니다. 아래 기존 구현 설명과 `project.html`은 V1 Fixture 기반 Workflow Prototype 기록이며, 현재 모델 기반 프로젝트1은 `SEHOOOOON/qa-agent-pipeline-v2`, 평가 프로젝트2는 `SEHOOOOON/agent-evaluation-framework`의 동명 브랜치에서 확인합니다. 메인 페이지의 형제 저장소 링크는 세 저장소를 함께 둔 로컬/클라우드 검토용입니다. 이 브랜치 저장은 main 반영이나 공개 사이트 배포가 아닙니다. 소개 페이지의 미커밋 수정은 검토본으로 보존하며 V1 제품·SRS·TC는 변경하지 않았습니다.

- **4-Agent · 4-Checkpoint** — 생성 역할과 검토 책임을 분리했습니다.
- **3-Tier QA 기준** — 공통 QA, 중앙제어 도메인, 기능별 품질 기준으로 TC를 설계합니다.
- **Playwright · Pytest 실행** — UI 동작과 내부 장치 상태를 함께 검증합니다.
- **5가지 비통과 원인 분류** — 제품 결함, 요구사항 확인, 환경, 자동화 코드, 조건 부족으로 구분합니다.
- **결과 정합성 검증** — Report·JSON·Run ID·포트폴리오 수치를 Checkpoint 4에서 교차 확인합니다.

## 검증 흐름

| 단계 | Agent | QA Checkpoint |
|------|-------|---------------|
| 1. 요구사항 정제 | 확정·추정·정보 부족 분리 | 테스트 가능한 범위와 보류 항목 판단 |
| 2. 테스트케이스 설계 | 3-Tier 기준으로 TC 작성 | 근거·독립성·명확성·자동화 적합성 심사 |
| 3. 자동화 실행 | Playwright로 승인 TC 실행 | 환경·재현 절차·수집 증거의 유효성 확인 |
| 4. 결과 분석·보고 | 비통과 원인과 Payload 생성 | Report·JSON·Run ID 대조 및 릴리즈 판단 |

## 무엇을 구현했나

**가상 중앙제어 시스템**

16대 장비의 모드·온도·잠금·장애·다중 제어 상태를 HTML 시뮬레이터로 구현했습니다.

**13건 통합 분류 파이프라인**

전체 13건을 실행해 Passed 8건, Failed 3건, Skipped 2건으로 집계하고 비통과 대표 사례를 5가지 QA 원인으로 분류합니다.

**Agent 4 · Checkpoint 4**

실행 결과를 규칙 기반으로 집계하고, 원본 Report와 JSON의 수치·TC ID·Run ID가 일치할 때만 Slack·Notion 보고 Payload를 생성합니다.

**구현 영상**

Agent 1~4 흐름, Playwright의 잠금 제어 검증, 영상용 정상 회귀 <code>12 passed</code>, Notion TC와 Slack 보고 화면을 순서대로 확인할 수 있습니다.

## 기술 스택

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=flat-square&logo=playwright&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)
![Slack](https://img.shields.io/badge/Slack-4A154B?style=flat-square&logo=slack&logoColor=white)
![Notion](https://img.shields.io/badge/Notion-000000?style=flat-square&logo=notion&logoColor=white)

## 실행 및 검증

~~~bash
pip install -r requirements.txt
playwright install chromium

python -m pytest
python scripts/agent4_reporting.py
python scripts/validate_outputs.py
~~~

- 통합 Run: **전체 13건 / Passed 8 / Failed 3 / Skipped 2**
- 분류 검증용 실패·보류 시나리오가 포함되어 전체 Pytest 결과는 의도적으로 FAILED입니다.
- Agent 4는 기본적으로 외부 변경이 없는 Dry-run으로 실행됩니다.
- 실제 Slack·Notion 전송은 환경변수 설정 후 <code>python scripts/agent4_reporting.py --send</code>에서만 수행합니다.
- 실행 결과가 FAILED여도 데이터 정합성이 맞으면 Checkpoint 4는 VALIDATED, 릴리즈 판단은 HOLD가 됩니다.

## 결과 확인

| 결과물 | 확인 내용 |
|--------|-----------|
| [Pytest HTML Report](reports/report.html) | 13건의 원본 실행 결과와 실패 상세 |
| [QA Results](reports/qa_results.json) | TC별 상태·실행시간·원인 분류 데이터 |
| [Agent 4 Summary](reports/agent4_summary.json) | 실행 집계, 5가지 QA 분류와 릴리즈 판단 |
| [Checkpoint 4 Validation](reports/checkpoint4_validation.json) | Report·JSON·Run ID 정합성 검증 결과 |
| [구현 영상](assets/playwright_pipeline_demo.mp4) | 자동 제어, 12 passed 로그, Notion·Slack 보고 화면 |

## 상세 문서

- [QA Pipeline Architecture](docs/architecture/QA_PIPELINE_ARCHITECTURE.md) — Agent·Checkpoint 역할과 데이터 흐름
- [3-Tier QA Criteria](docs/architecture/agent2_3tier_qa_criteria.md) — 공통·도메인·기능 품질 기준
- [Production Adoption Considerations](docs/architecture/production_adoption_considerations.md) — 실무 도입 시 한계와 통제 방안
- [Traceability Matrix](docs/samples/traceability_matrix.md) — 요구사항·TC·자동화·Finding 추적성
- [Interview Points](docs/interview/PORTFOLIO_INTERVIEW_POINTS.md) — 프로젝트 의도와 예상 면접 질문

## 프로젝트 구조

~~~text
qa-agent-pipeline/
├─ assets/                   # 구현 영상
├─ docs/                     # 설계·면접·샘플 문서
├─ reports/                  # 실행 결과만 보관
├─ scripts/                  # 결과 분석·검증 실행 도구
│  ├─ agent4_reporting.py    # Agent 4 집계·분류·외부 보고
│  └─ validate_outputs.py    # Checkpoint 4 산출물 교차 검증
├─ tests/                    # Playwright 테스트
├─ .gitignore                # 비공개·로컬 파일 제외
├─ README.md                 # 프로젝트 소개·실행·구조 안내
├─ index.html                # 포트폴리오 대표 홈
├─ project.html              # 프로젝트 상세 페이지
├─ virtual-controller.html   # 가상 관제 시뮬레이터
├─ pytest.ini                # Pytest 결과 생성 설정
└─ requirements.txt          # Python 의존성
~~~
