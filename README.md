<div align="center">

<!-- 2026-10-11 브랜치 보존: 오늘 편집한 메인·P1·P2 소개/상세는 세 저장소의 codex/night-review-20261009에서 확인. 현재 작업본을 보존하며 추가 문구/디자인 수정·main 병합·사이트 배포는 하지 않음. 포폴 검사49 PASS, Git에 포함되는 로컬 파일 링크89개 확인. -->

<!-- 2026-10-10: 기존 야간 검토 브랜치를 제출 후보로 유지. V1 실행 코드·기준 자산은 수정하지 않음. -->
<!-- 2026-10-10 최종 편집: 메인 역할·결과 문구 정리. P2 포폴 23개 및 세 페이지 9화면/251파일 확인. 실행 코드·경력 사실 미변경, 공개 배포 전. 상세 기록은 P1 PROJECT_HANDOFF와 P2 IMP-006에 보존. -->

<h1>QA 판단 기준 기반 Multi-Agent Workflow</h1>

<p>요구사항 정제부터 테스트 설계, Playwright 실행, 비통과 원인 분류와 보고까지<br/>QA 변경 검증 흐름을 4개의 Agent와 4개의 Checkpoint로 구조화한 개인 프로젝트입니다.</p>

[![포트폴리오 홈](https://img.shields.io/badge/Portfolio-Home-58A6FF?style=for-the-badge&labelColor=0b1220)](https://SEHOOOOON.github.io/qa-agent-pipeline/)
[![프로젝트 상세](https://img.shields.io/badge/Project-Detail-58A6FF?style=for-the-badge&labelColor=0b1220)](https://SEHOOOOON.github.io/qa-agent-pipeline/project.html)
[![가상 관제 화면](https://img.shields.io/badge/Live-Simulator-58A6FF?style=for-the-badge&labelColor=0b1220)](https://SEHOOOOON.github.io/qa-agent-pipeline/virtual-controller.html)

<p><b>작업 브랜치 미리보기</b> (<code>claude/fixes-20261015</code>, 공개 사이트 반영 전)</p>

[![메인 포트폴리오](https://img.shields.io/badge/%EB%A9%94%EC%9D%B8_%ED%8F%AC%ED%8A%B8%ED%8F%B4%EB%A6%AC%EC%98%A4-%EC%97%B4%EA%B8%B0-2ea44f?style=for-the-badge&labelColor=0b1220)](https://raw.githack.com/SEHOOOOON/qa-agent-pipeline/claude/fixes-20261015/main.html)
[![프로젝트1 소개](https://img.shields.io/badge/%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B81_%EC%86%8C%EA%B0%9C-%EC%97%B4%EA%B8%B0-2ea44f?style=for-the-badge&labelColor=0b1220)](https://raw.githack.com/SEHOOOOON/qa-agent-pipeline-v2/claude/fixes-20261015/project.html)
[![프로젝트2 소개](https://img.shields.io/badge/%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B82_%EC%86%8C%EA%B0%9C-%EC%97%B4%EA%B8%B0-2ea44f?style=for-the-badge&labelColor=0b1220)](https://raw.githack.com/SEHOOOOON/agent-evaluation-framework/claude/fixes-20261015/portfolio/index.html)
[![프로젝트2 평가 결과](https://img.shields.io/badge/%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B82_%ED%8F%89%EA%B0%80_%EA%B2%B0%EA%B3%BC-%EC%97%B4%EA%B8%B0-2ea44f?style=for-the-badge&labelColor=0b1220)](https://raw.githack.com/SEHOOOOON/agent-evaluation-framework/claude/fixes-20261015/portfolio/report.html)

<sub>각 페이지는 바로 열립니다. 페이지 안의 다른 페이지 이동 버튼은 세 저장소를 PC에 나란히 둔 경우 기준이라, 웹 미리보기에서는 이 버튼들로 이동하세요.</sub>


</div>

---

> AI가 만든 산출물을 그대로 신뢰하지 않습니다.<br/>
> 각 단계의 입력·출력과 판단 근거를 QA Checkpoint에서 검토한 뒤 다음 단계로 전달합니다.

## 프로젝트 한눈에 보기

> **야간 검토본 안내 (2026-10-09)**: `codex/night-review-20261009`의 `index.html`은 최신 메인 소개 페이지입니다. 아래 기존 구현 설명과 `project.html`은 V1 Fixture 기반 Workflow Prototype 기록이며, 현재 모델 기반 프로젝트1은 `SEHOOOOON/qa-agent-pipeline-v2`, 평가 프로젝트2는 `SEHOOOOON/agent-evaluation-framework`의 동명 브랜치에서 확인합니다. 메인 페이지의 형제 저장소 링크는 세 저장소를 함께 둔 로컬/클라우드 검토용입니다. 이 브랜치 저장은 main 반영이나 공개 사이트 배포가 아닙니다. 2026-10-10에는 세 페이지의 표현·배치와 공개용 근거를 정리해 이 브랜치의 제출 후보로 보존했습니다. 메인/P1/P2는 같은 이름의 브랜치를 기준으로 확인하며, V1 제품·SRS·TC는 변경하지 않았습니다. 공개 배포와 실제 제출 URL 확인은 별도입니다.

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

## 2026-10-10 · 소개 문구 검토

담당 업무·개인 프로젝트 소개를 구체적인 행동 중심으로 정리했습니다. 회사 업무와 개인 프로젝트, 로컬 반복 검사와 실제 AI 평가를 구분하고 경력·성과 수치는 추가하지 않았습니다. 구조·링크·CSS는 유지했습니다. 세 페이지의 1440/768/390px 화면, 링크 대상 251개와 P2 포폴 검사 28개를 확인했습니다. 원문 비교·백업·화면 검증은 형제 P1 `runs/manual_checks/submission-20261010/natural-copy/`에 보존했으며 이 폴더는 로컬 검토 자료입니다. API·커밋·푸시·배포는 하지 않았습니다.

## 2026-10-10 · 개인 프로젝트 소개 간격

수정 전에는 목록의 21px 간격과 문단의 22px 위쪽 여백이 겹쳐 제목과 설명이 43px 떨어졌습니다. 해당 제목 바로 다음 문단에만 간격을 12px로 조정했습니다. 1440·768·390px에서 간격과 가로 넘침을 검사했으며, 카드 내부 설명의 여백은 유지했습니다. 본문·링크·실행 로직은 변경하지 않았습니다. 원본 백업과 검사 결과는 형제 P1의 `runs/manual_checks/submission-20261010/main-spacing/`에 보존했습니다.

<!-- 2026-10-10 최종 로컬 검수: 소개/Agent 3 비교 범위 문구 정리. 원본 점수·실무 경력 미변경. 3페이지 12화면 및 제출 사본 검사. 상세 수정 전후와 한계는 최신 P1 인계 및 P2 IMP-006 참조. 커밋·배포 전. -->

## 2026-10-11 · 메인 프로젝트 카드 요약

메인 P1/P2 카드의 긴 실행 사례·한계 설명과 항목 목록·태그를 빼고, 제목·두 문장 소개·상세 페이지 버튼으로 형식을 맞췄습니다. 실무 카드의 자료 공개 안내와 반복되는 담당 범위 문장도 삭제했습니다. 세부 결과를 메인에서 덜어내며 지원 범위가 넓게 읽힐 위험을 고려해 P1의 가상 중앙제어 환경과 단계별 검토 역할은 유지했습니다. P1/P2 상세 페이지와 원본 수치·근거는 수정하지 않았습니다.

수정·검증일은 2026-10-11 KST입니다. 수정 전 메인은 `index.before-card-summary-20261011.html`로 보존했습니다. Sites 로컬 편집 절차로 전후 화면을 대조했고, 1440·768·390px에서 넘침·JS 오류 없음, 두 개인 카드의 동일한 구조, 상세 링크 HTTP 200, 나머지 본문·실무 경력·스크립트·링크 및 상세 페이지 해시 보존을 확인했습니다. 기존 P2 포폴 검사 47건도 통과했습니다. 검증 자료는 형제 P1 `runs/manual_checks/main-card-summary-20261011/`에 있습니다. 첫 패치는 변경 위치 순서 때문에 적용 전에 실패했고, 순서를 바로잡아 적용했습니다. 런타임 검사·AI 호출·외부 전송·커밋·푸시·배포는 하지 않았습니다.

## 2026-10-11 · 메인 개인 프로젝트 소개의 배경 보강

두 문장 요약으로 개발 동기가 드러나지 않는다는 사용자 피드백에 따라 P1/P2 소개만 각각 두 문단·네 문장으로 보완했습니다. 첫 문단은 실무에서 반복했던 QA 업무와 평가 도구를 만든 이유, 두 번째 문단은 구현 내용과 확인한 결과를 설명합니다. 개별 실패 수치·수정 이력·한계 목록은 다시 넣지 않았으며, AI 검토와 사람의 최종 등록 역할을 유지했습니다. 자동화 범위가 과장될 위험을 고려해 가상 환경을 명시하고 수동 대비 시간 절감이나 새 요청의 안정성을 입증했다고 쓰지 않았습니다.

수정·검증일 2026-10-11 KST. 수정 전 `index.before-intro-depth-20261011.html`을 보존했습니다. 소개 문단을 제외한 DOM·링크·스타일·스크립트 동일성, 1440/768/390px 넘침·JS 오류 없음, 상세 링크 HTTP 200을 확인했습니다. 두 카드의 PC/모바일 캡처 확인 및 포폴 검사49 PASS. 결과는 형제 P1 `runs/manual_checks/main-intro-depth-20261011/{verification.json,portfolio-tests.xml,verify.py,*.png}`에 있습니다. 수정 후 index.html SHA-256은 `1ff071f7aa2aa2b612291e5d5e25efde29059e6dfbaf1498ac642aedb1149f96`입니다. Sites의 로컬 편집 경로로 검증했으며 상세 페이지·실무 경력·운영 코드·공식 자산·API·외부 전송·커밋·푸시·배포는 변경하거나 수행하지 않았습니다. 실제 독자의 이해도와 공개 URL 검증은 별도입니다.
