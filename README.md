<div align="center">

# 중앙제어 도메인 기반 Multi-Agent QA Workflow

**Agent가 결과물을 생성하고, QA Checkpoint가 품질을 통제합니다.**  
각 단계의 결과가 정의된 기준을 통과한 경우에만 다음 단계로 전달되도록 구성했습니다.

[![가상 관제 화면](https://img.shields.io/badge/가상_관제_화면-58A6FF?style=for-the-badge&labelColor=0D1117)](https://SEHOOOOON.github.io/qa-agent-pipeline/virtual-controller.html)
[![포트폴리오](https://img.shields.io/badge/포트폴리오_페이지-3FB950?style=for-the-badge&labelColor=0D1117)](https://SEHOOOOON.github.io/qa-agent-pipeline/)
[![GitHub](https://img.shields.io/badge/GitHub_Repository-8B949E?style=for-the-badge&logo=github&logoColor=white&labelColor=0D1117)](https://github.com/SEHOOOOON/qa-agent-pipeline)

</div>

---

## 이 프로젝트를 만든 이유

중앙제어 시스템 QA를 수행하면서 같은 요구사항도 검토자의 경험과 관점에 따라 테스트 범위가 달라지고, 머릿속에 있는 판단 기준을 매번 문서와 테스트케이스에 다시 풀어내야 하는 문제를 반복해서 경험했습니다.

AI를 활용하면 테스트케이스를 빠르게 만들 수 있었지만, 요구사항에 없는 색상·문구·상태값까지 그럴듯하게 확정하거나, 정보가 부족한 항목을 정상적인 Pass/Fail 기준처럼 작성하는 문제가 생겼습니다. 단순히 Agent 수를 늘리거나 TC 생성량을 높이는 방식으로는 제가 원하는 QA 품질을 유지하기 어렵다고 판단했습니다.

그래서 이 프로젝트는 **개인의 QA 경험을 대신하는 AI**가 아니라, 제가 중요하게 생각하는 QA 판단 기준을 명시적으로 구조화하고 반복 적용하기 위해 시작했습니다. 각 Agent가 결과물을 생성하되, 단계별 `QA Checkpoint`가 근거·명확성·실행 가능성·보고 일관성을 확인하고, 기준을 충족한 결과만 다음 단계로 전달하도록 설계했습니다.

> **프로젝트 목표:** 요구사항 정제부터 테스트 설계, 자동화 실행과 결과 보고까지 동일한 QA 기준이 끊기지 않도록 연결하고, AI의 추측이 다음 결과물로 전파되는 것을 구조적으로 줄이는 것

## 프로젝트 개요

이 프로젝트는 다음 원칙을 반복적으로 적용합니다.

- 요구사항을 바로 TC로 변환하지 않음
- 확정 정보와 추가 확인 정보를 먼저 분리
- 공통·도메인·기능별 3단계 QA 기준 적용
- 각 단계의 결과물을 QA Checkpoint에서 검토
- Checkpoint를 통과한 기대결과만 자동화 실행으로 연결
- UI 표시값과 가상 Register 상태를 각각 검증
- 모든 실패를 원인별로 분류하고 후속 조치를 구분

> **핵심 구조:** Agent는 결과물을 생성하고, QA Checkpoint는 다음 단계로 전달 가능한 품질인지 판단합니다.

---

## 핵심 설계 개념 · QA Checkpoint

Checkpoint는 반드시 별도의 AI Agent를 의미하지 않습니다. Agent의 결과를 다음 단계로 전달하기 전에, 정의된 기준으로 품질을 확인하는 **판정 지점과 검사 절차 전체**를 의미합니다.

- Checkpoint 1: Agent 1 + 요구사항 충분성 규칙
- Checkpoint 2: TC Review Sub-Agent + TC 품질 기준
- Checkpoint 3: Pytest·Playwright의 결정론적 실행 검증
- Checkpoint 4: 집계 로직과 보고 결과 일관성 검증

이 프로젝트에서는 단순한 통과·차단보다 **점검 → 판정 → 수정 반환 → 재검토**의 흐름을 강조하기 위해 `Gate` 대신 `QA Checkpoint`라는 표현을 사용합니다.

---

## 전체 처리 흐름

```text
요구사항과 참고 문서
  ↓
Agent 1 · 요구사항 정제
  ↓ Checkpoint 1 · 요구사항 충분성
Agent 2 · 테스트케이스 설계
  ↓ Checkpoint 2 · TC 품질 적합성
Agent 3 · Playwright 자동화 실행
  ↓ Checkpoint 3 · 실행 결과 신뢰성
Agent 4 · 결과 분석·보고
  ↓ Checkpoint 4 · 보고 결과 일관성
Slack 알림 · Notion TC 목록 · 실행 리포트
```

---

## 단계별 QA Checkpoint

### Checkpoint 1 · 요구사항 충분성

- 확정 정보·추정 정보·정보 부족이 구분됐는가?
- 근거 출처와 테스트 가능 범위가 명확한가?
- Agent 2가 사용하면 안 되는 항목이 표시됐는가?
- 전체 진행·일부 진행·확인 후 진행 판정이 있는가?

### Checkpoint 2 · TC 품질 적합성

- 요구사항에 없는 기대결과를 만들지 않았는가?
- 정보 부족 항목을 Pass/Fail 기준으로 사용하지 않았는가?
- UI Assert와 Register Assert가 구체적인가?
- Initial State·Setup·Cleanup이 있는가?
- 단독 실행과 자동화 코드 변환이 가능한가?

판정: `승인` · `수정 후 재검토` · `검증 가능 범위만 승인` · `요구사항 확인 필요` · `실행 대상 제외`

### Checkpoint 3 · 실행 결과 신뢰성

- 사전 환경 점검과 테스트 초기화를 통과했는가?
- 필요한 UI·Register Assert가 실제로 수행됐는가?
- 실패 시 Screenshot·Trace·Register Snapshot이 존재하는가?
- 자동화 코드 문제와 제품 동작 문제를 구분할 근거가 있는가?
- 미실행 항목이 제품 Fail로 잘못 집계되지 않았는가?

### Checkpoint 4 · 보고 결과 일관성

- 실제 실행 수치와 보고 수치가 일치하는가?
- 각 실패에 분류 근거와 후속 조치가 있는가?
- 관련 TC와 실행 증거가 연결됐는가?
- Slack·Notion 전송 실패가 원본 테스트 결과를 변경하지 않는가?
- 배포 권고안에 판단 근거가 있는가?

---

## 3단계 QA 기준

### 1단계 · 공통 QA 기준

정상·예외·경계값·상태 변경·회귀 영향·정보 부족·명확한 Pass/Fail 기준

### 2단계 · 중앙제어 도메인 기준

UI·Register 정합성, 제어값·상태값, 운전 모드, 통신, 알람, Lock·인터록, 다중 장비, 비대상 상태 유지

### 3단계 · 기능별 품질 기준

적용 조건, 구체적 기대결과, Pass/Fail, 제외 항목, 자동화 가능 여부, 관련 TC 연결

---

## UI·Register 정합성 자동 검증

Playwright를 활용해 UI 표시값과 가상 Register의 내부 장치 상태를 각각 확인합니다.

```text
UI Assert
- 운전 모드, 설정온도, Lock, 알람·통신 상태
- 제어 버튼 활성·비활성 상태

Register Assert
- devices[id].mode
- devices[id].setTemp
- devices[id].locked
- devices[id].online
```

두 계층이 함께 변경되는 제어 TC에는 UI Assert와 Register Assert를 모두 적용합니다.

---

## 테스트 결과 5가지 분류

1. **제품 결함 후보** — 정상 조건에서도 실제 동작이 기대값과 다름
2. **기획·요구사항 확인 필요** — 기대결과가 정의되지 않아 판정 불가
3. **환경·시뮬레이터 문제** — 응답·초기화·데이터 문제로 검증 불가
4. **자동화 코드 문제** — Selector·대기·실행 순서 문제
5. **조건 부족으로 미실행** — 필수 데이터·계정·Mock·선행 조건 부족

---

## 현재 구현 범위

| 구분 | 상태 |
|---|---|
| 가상 중앙제어 시스템 | 16대 장비 제어 시뮬레이터 구현 |
| Agent 1 | 요구사항 정제 기준과 출력 구조 정의 |
| Agent 2 | 3단계 QA 기준 기반 TC 설계 구조 정의 |
| Checkpoint 2 | TC Review Sub-Agent 기준 정의 |
| Agent 3 | Python·Pytest·Playwright 테스트 코드 구성 |
| Notion | 생성 TC 목록 등록 확인 |
| Slack | 테스트 결과 알림 수신 확인 |
| 실행 증거 | 클린 환경 검증과 캡처 정리 완료 |

---

## 저장소 구조

```text
qa-agent-pipeline/
├── docs/                         # 에이전트 프롬프트 및 산출물 샘플
│   ├── agent1_requirement_analyst.md
│   ├── agent2_tc_designer.md
│   ├── agent2_sub_tc_reviewer.md
│   ├── agent1_output_sample.md
│   ├── agent2_tc_list_sample.md
│   ├── gate2_review_loop_sample.md
│   └── traceability_matrix.md
├── tests/                        # Playwright 자동화 테스트 스크립트
│   ├── test_controller.py
│   └── conftest.py
├── reports/                      # Agent 4 리포팅 결과물
│   ├── qa_results.json
│   └── report.html
├── virtual-controller.html
├── notify_agent.py
├── requirements.txt
├── ARCHITECTURE_TRADEOFFS.md
└── README.md
```

실제 저장소 구조가 변경되면 위 트리도 함께 업데이트합니다.

---

## 실행 방법

```bash
git clone https://github.com/SEHOOOOON/qa-agent-pipeline.git
cd qa-agent-pipeline
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
playwright install chromium
pytest tests/test_controller.py -v --browser chromium
```

화면을 보면서 실행:

```bash
pytest tests/test_controller.py -v --browser chromium --headed
```

HTML 리포트 생성:

```bash
pytest tests/test_controller.py -v --browser chromium --html=reports/report.html --self-contained-html
```

---

## 요구사항부터 결과까지의 연결

```text
REQ-MODE-001
  ↓ RULE-MODE-002
  ↓ TC-MODE-002
  ↓ test_fan_mode_temperature_disabled()
  ↓ RUN-001
  ↓ PASS / BUG / REVIEW / ENV / AUTOMATION / BLOCKED
```

---

## 현재 확인된 한계점

1. 모든 Agent 분석을 매 실행마다 수행하면 지연과 토큰 비용이 증가할 수 있습니다.
2. 실행 시점마다 코드를 자유롭게 생성하면 재현성이 낮아질 수 있습니다.
3. 브라우저 기반 가상 시스템이므로 실제 H/W 결함 진단은 범위에 포함하지 않습니다.
4. 같은 AI 모델이 생성하고 검토하면 논리적 맹점을 공유할 수 있습니다.

자세한 내용은 [`ARCHITECTURE_TRADEOFFS.md`](./ARCHITECTURE_TRADEOFFS.md)에서 확인할 수 있습니다.

---

## 주요 결과물

- [가상 중앙제어 화면](https://SEHOOOOON.github.io/qa-agent-pipeline/virtual-controller.html)
- [포트폴리오 페이지](https://SEHOOOOON.github.io/qa-agent-pipeline/)
- [요구사항 정제 기준](./docs/agent1_requirement_analyst.md)
- [TC 설계 기준](./docs/agent2_tc_designer.md)
- [TC 품질 검토 기준](./docs/agent2_sub_tc_reviewer.md)
- [Playwright 자동화 코드](./tests/test_controller.py)
- [한계점과 설계 선택](./ARCHITECTURE_TRADEOFFS.md)
- [추적성 매트릭스](./docs/traceability_matrix.md)

---

<div align="center">

**Central Control · QA Checkpoint Workflow**  
Python · Pytest · Playwright · Slack · Notion

</div>
