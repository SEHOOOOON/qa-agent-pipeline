<div align="center">

<h1>QA 판단 기준 기반 Multi-Agent Workflow</h1>

<p>요구사항 분석부터 시험 설계, 실제 화면 시험, 결과 보고까지 QA 변경 검증 흐름을 AI Agent로 구조화하고,<br/>그 Agent들이 기준대로 일하는지를 별도 도구로 평가한 개인 프로젝트 포트폴리오입니다.</p>

<p><b>포트폴리오 바로 보기</b></p>

[![메인 포트폴리오](https://img.shields.io/badge/%EB%A9%94%EC%9D%B8_%ED%8F%AC%ED%8A%B8%ED%8F%B4%EB%A6%AC%EC%98%A4-%EC%97%B4%EA%B8%B0-2ea44f?style=for-the-badge&labelColor=0b1220)](https://sehooooon.github.io/qa-agent-pipeline/main.html)
[![프로젝트1 소개](https://img.shields.io/badge/%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B81_%EC%86%8C%EA%B0%9C-%EC%97%B4%EA%B8%B0-2ea44f?style=for-the-badge&labelColor=0b1220)](https://sehooooon.github.io/qa-agent-pipeline-v2/project.html)
[![프로젝트2 소개](https://img.shields.io/badge/%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B82_%EC%86%8C%EA%B0%9C-%EC%97%B4%EA%B8%B0-2ea44f?style=for-the-badge&labelColor=0b1220)](https://sehooooon.github.io/agent-evaluation-framework/portfolio/index.html)
[![프로젝트2 평가 결과](https://img.shields.io/badge/%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B82_%ED%8F%89%EA%B0%80_%EA%B2%B0%EA%B3%BC-%EC%97%B4%EA%B8%B0-2ea44f?style=for-the-badge&labelColor=0b1220)](https://sehooooon.github.io/agent-evaluation-framework/portfolio/report.html)

<sub>세 페이지는 상단 메뉴로 서로 이동할 수 있습니다. 프로젝트1에는 대표 사례를 실제 화면으로 녹화한 약 1분 영상이 있습니다.</sub>

</div>

---

> AI가 만든 산출물을 그대로 신뢰하지 않습니다.<br/>
> 단계마다 자동 검사와 근거 검토를 거치고, 최종 등록은 사람이 결정합니다. 그리고 Agent 자체를 별도 도구로 평가합니다.

## 저장소 구성

| 저장소 | 내용 |
|---|---|
| **qa-agent-pipeline** (이 저장소) | 포트폴리오 메인 페이지(`main.html`), 가상 관제 화면, 초기 V1 시제품 |
| [qa-agent-pipeline-v2](https://github.com/SEHOOOOON/qa-agent-pipeline-v2) · 프로젝트 1 | 변경 요청을 받아 Agent 1~4가 분석·시험 설계·실제 화면 시험·보고를 하고 사람이 최종 승인하는 QA 파이프라인 |
| [agent-evaluation-framework](https://github.com/SEHOOOOON/agent-evaluation-framework) · 프로젝트 2 | 프로젝트 1의 Agent들이 기준대로, 일관되게 일하는지 평가하고 찾은 문제를 개선 보고서로 남기는 평가 도구 |

## 프로젝트 1 · QA Agent Pipeline V2

- **흐름**: Agent 1 요구사항 분석 → Agent 2 시험 설계(기존 TC 재사용·고쳐 쓰기 판단) → Agent 3 자동화·실제 화면 시험·원상 복원 → Agent 4 결과 분류·보고 → 사람 최종 판단.
- **안전장치**: 단계마다 자동 검사(Checkpoint)와 AI 근거 검토, 애매한 요구사항은 추측하지 않고 질문을 남기고 멈춤, SRS 수정과 공식 TC 등록은 사람 승인 때만.
- **최근 결과**: 대표 요청 5개 중 4개(전원·풍량·모드·온도)는 끝까지 실행했고 잠금은 정책이 정해지지 않아 질문을 남기고 멈췄습니다(의도한 동작). 또 시험 설계를 시나리오별 3번 반복해 전원·풍량·모드는 3번 모두 같은 정답 구조가 나왔습니다.

## 프로젝트 2 · Agent Evaluation Framework

- **평가**: 26개 기준(0~5점). 사람이 확정한 정답지가 있는 부분은 코드가, 나머지는 생성과 다른 회사의 AI(Claude)가 근거 번호를 골라 채점하고, 사람 대조로 채점을 검증합니다(누적 27개 중 23개 일치).
- **개선 절차**: 문제를 찾으면 발견 → 사람 확인 → 재발 확인 → 원인 → 수정 → 재검증 순서로 사례마다 보고서를 남깁니다.
- **사례**: 온도 시험 설계가 준비 단계에서 바꾼 모드의 복원 확인을 빠뜨리는 문제를 4번 중 4번 찾아, 원인인 프로젝트 1의 계약까지 고친 뒤 3번 중 3번 포함으로 확인했습니다.

## 초기 V1 시제품 (2026-07~08)

이 저장소의 실행 코드는 프로젝트 1 이전에 만든 시제품입니다. AI 호출 없이 미리 만든 산출물(Fixture)로 4-Agent · 4-Checkpoint 흐름을 검증했습니다.

- 16대 장비의 모드·온도·잠금·장애 상태를 HTML 시뮬레이터(`virtual-controller.html`)로 구현했습니다.
- Playwright·Pytest로 13건을 실행해 Passed 8 / Failed 3 / Skipped 2로 집계하고, 비통과를 5가지 원인(제품 결함, 요구사항 확인, 환경, 자동화 코드, 조건 부족)으로 분류했습니다. 분류 검증용 실패가 포함되어 있어 전체 결과는 의도적으로 FAILED입니다.
- Agent 4는 결과를 규칙 기반으로 집계하고, Report·JSON·Run ID가 일치할 때만 Slack·Notion 보고 내용을 만듭니다(기본은 미리보기, `--send`일 때만 전송).

~~~bash
pip install -r requirements.txt
playwright install chromium

python -m pytest
python scripts/agent4_reporting.py
python scripts/validate_outputs.py
~~~

| 자료 | 내용 |
|---|---|
| [Pytest 보고서](reports/report.html) · [QA 결과](reports/qa_results.json) | 13건 실행 결과와 실패 상세 |
| [Agent 4 요약](reports/agent4_summary.json) · [Checkpoint 4 검증](reports/checkpoint4_validation.json) | 집계·분류·릴리즈 판단, 산출물 정합성 |
| [구현 영상](assets/playwright_pipeline_demo.mp4) | 자동 제어, 실행 로그, Notion·Slack 보고 화면 |
| [V1 설계 문서](docs/architecture/QA_PIPELINE_ARCHITECTURE.md) · [3-Tier QA 기준](docs/architecture/agent2_3tier_qa_criteria.md) · [추적성 표](docs/samples/traceability_matrix.md) | V1 당시의 설계·기준·샘플 (현재 프로젝트 1과 구조가 다름) |

## 기술 스택

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=flat-square&logo=playwright&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI_API-412991?style=flat-square&logo=openai&logoColor=white)
![Claude](https://img.shields.io/badge/Claude_API-D97757?style=flat-square&logo=anthropic&logoColor=white)
![Slack](https://img.shields.io/badge/Slack-4A154B?style=flat-square&logo=slack&logoColor=white)
![Notion](https://img.shields.io/badge/Notion-000000?style=flat-square&logo=notion&logoColor=white)
